from typing import Optional
import io

def extract_pdf_text_pdfium(pdf_bytes: bytes) -> str:
    # Primary: PyMuPDF
    import fitz  # PyMuPDF
    text_parts = []
    with fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()

def extract_pdf_text_pypdf(pdf_bytes: bytes) -> str:
    # Fallback: PyPDF
    from pypdf import PdfReader
    text_parts = []
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for p in reader.pages:
        text_parts.append(p.extract_text() or "")
    return "\n".join(text_parts).strip()

def extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        txt = extract_pdf_text_pdfium(pdf_bytes)
        if txt.strip():
            return txt
    except Exception:
        pass
    try:
        txt = extract_pdf_text_pypdf(pdf_bytes)
        if txt.strip():
            return txt
    except Exception:
        pass
    return ""
