from typing import List, Dict, Any
from .llm_client import chat_complete

SYSTEM = (
    "You are a clinical summarization assistant. "
    "Write concise, factual summaries. Do NOT invent facts. If unsure, say so."
)

TEMPLATE = """Create a concise diagnostic summary using BOTH the clinical notes and the imaging findings.

Include:
- Chief complaint & HPI
- Pertinent PMH/PSH/Allergies
- Medications
- Pertinent labs/imaging
- Assessment & Plan (bullet points)

Clinical Notes:
{notes}

Imaging Findings (structured):
{imaging_findings}
"""

def summarize_notes(notes: str, imaging_findings: List[str] | None = None) -> dict:
    imaging_findings = imaging_findings or []
    prompt = TEMPLATE.format(
        notes=(notes or "").strip(),
        imaging_findings="\n".join(f"- {f}" for f in imaging_findings) or "- (none provided)"
    )
    out = chat_complete(SYSTEM, prompt, temperature=0.2)
    return {"summary": out, "citations": []}
