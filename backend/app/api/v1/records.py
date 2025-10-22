from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from backend.app.services.summarizer import summarize_notes
from backend.app.utils.pdf_extractor import extract_pdf_text
from backend.app.core.security import require_role

router = APIRouter()


class SummarizeIn(BaseModel):
    text: str
    imaging_findings: Optional[List[str]] = None


@router.post("/records/summarize", dependencies=[Depends(require_role("clinician", "admin"))])
def summarize(in_: SummarizeIn):
    """Summarize clinical notes (optionally with imaging findings)."""
    return summarize_notes(in_.text, in_.imaging_findings or [])


@router.post("/records/extract_pdf", dependencies=[Depends(require_role("clinician", "admin", "patient"))])
async def extract_pdf(file: UploadFile = File(...)):
    """Extract plain text from a PDF."""
    if not file.content_type or "pdf" not in file.content_type:
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    data = await file.read()
    text = extract_pdf_text(data)
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")
    return {"text": text[:200_000]}  # safety cap
