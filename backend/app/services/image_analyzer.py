from typing import Dict, Any
import io, numpy as np
from PIL import Image
import torch
import torchxrayvision as xrv
from skimage.transform import resize
import pydicom

# Load once (global)
_model = None
_transform = None
_LABELS = None

def _init_model():
    global _model, _transform, _LABELS
    if _model is None:
        _model = xrv.models.DenseNet(weights="densenet121-res224-all")  # 18 findings
        _model.eval()
        _transform = xrv.datasets.XRayCenterCrop()  # simple center crop + normalize
        _LABELS = list(_model.pathologies)
    return _model, _transform, _LABELS

def _load_as_float32_grayscale(img: Image.Image) -> np.ndarray:
    img = img.convert("L")  # grayscale
    arr = np.asarray(img).astype(np.float32)
    # normalize to 0..1
    if arr.max() > 1.0:
        arr /= 255.0
    # model expects 224x224
    arr = resize(arr, (224, 224), preserve_range=True, anti_aliasing=True).astype(np.float32)
    return arr

def _dicom_to_pil(dcm_bytes: bytes) -> Image.Image:
    ds = pydicom.dcmread(io.BytesIO(dcm_bytes))
    arr = ds.pixel_array.astype(np.float32)
    # rescale if present
    if hasattr(ds, "RescaleSlope") and hasattr(ds, "RescaleIntercept"):
        arr = arr * float(ds.RescaleSlope) + float(ds.RescaleIntercept)
    arr = arr - arr.min()
    if arr.max() > 0:
        arr = arr / arr.max()
    arr = (arr * 255.0).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def analyze_image_bytes(img_bytes: bytes, filename: str | None = None) -> Dict[str, Any]:
    """
    Returns model probabilities for common chest x-ray findings, plus top findings.
    Supports PNG/JPG and DICOM (.dcm).
    """
    # Load as PIL image (handle DICOM)
    if filename and filename.lower().endswith(".dcm"):
        pil = _dicom_to_pil(img_bytes)
    else:
        pil = Image.open(io.BytesIO(img_bytes))

    w, h = pil.size

    # Prepare tensor
    arr = _load_as_float32_grayscale(pil)         # HxW in 0..1
    img_tensor = torch.from_numpy(arr)[None, None, :, :]  # [B, C, H, W]
    img_tensor = (img_tensor - img_tensor.mean()) / (img_tensor.std() + 1e-8)  # z-norm

    # Inference
    model, _, labels = _init_model()
    with torch.no_grad():
        out = model(img_tensor)                   # logits
        probs = torch.sigmoid(out)[0].cpu().numpy().tolist()

    # Create label→prob mapping and top-5 findings (threshold 0.5 for MVP)
    findings = [{ "label": l, "prob": float(p) } for l, p in zip(labels, probs)]
    top = sorted(findings, key=lambda x: x["prob"], reverse=True)[:5]
    pos = [f["label"] for f in findings if f["prob"] >= 0.5]

    # Friendly text list for the summarizer to ingest
    textual = [f'{f["label"]}: {f["prob"]:.2f}' for f in top]
    if pos:
        textual.insert(0, "Positive findings (p>=0.5): " + ", ".join(pos))

    return {
        "modality": "chest-xray (inferred)",
        "shape": [w, h],
        "top5": top,
        "positive": pos,
        "findings": textual if textual else ["No strong positive findings"],
    }
