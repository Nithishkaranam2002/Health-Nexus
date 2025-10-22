from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.app.services.image_analyzer import analyze_image_bytes
from backend.app.core.security import require_role

router = APIRouter()


@router.post("/images/analyze", dependencies=[Depends(require_role("clinician", "admin"))])
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts PNG, JPG, JPEG, or DICOM (.dcm) files and returns AI analysis.
    Relaxed content-type check to handle browser quirks.
    """
    filename = file.filename or "uploaded_image"
    content_type = file.content_type or ""

    allowed_types = ["image/png", "image/jpeg", "application/dicom", "application/octet-stream"]
    if not (any(t in content_type for t in allowed_types) or filename.lower().endswith(".dcm")):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Please upload PNG, JPG, or DICOM.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        return analyze_image_bytes(data, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {e}")
