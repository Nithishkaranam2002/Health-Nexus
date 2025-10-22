from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.services.chatbot import answer
from backend.app.core.security import require_role

router = APIRouter()


class ChatIn(BaseModel):
    message: str
    notes: Optional[str] = None
    imaging_findings: Optional[List[str]] = None


@router.post("/chat", dependencies=[Depends(require_role("clinician", "patient", "admin"))])
def chat(in_: ChatIn):
    """General QA over optional case context (notes + imaging findings)."""
    resp = answer(in_.message, notes=in_.notes, imaging_findings=in_.imaging_findings or [])
    return {"reply": resp}
