from .llm_client import chat_complete

SYSTEM = (
    "You are a clinical summarization assistant. "
    "Write concise, factual, and cited summaries from the provided notes. "
    "Use neutral tone. Do NOT invent facts. If unsure, say so."
)

TEMPLATE = """Summarize the following de-identified clinical notes into:
- Chief complaint & HPI
- Pertinent PMH/PSH/Allergies
- Medications
- Pertinent labs/imaging
- Assessment & Plan (bullet points)

Notes:
{notes}
"""

def summarize_notes(notes: str) -> dict:
    prompt = TEMPLATE.format(notes=notes.strip())
    out = chat_complete(SYSTEM, prompt, temperature=0.2)
    # MVP: fake citations; later, add RAG to produce real ones
    return {"summary": out, "citations": []}
