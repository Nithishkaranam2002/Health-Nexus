from .llm_client import chat_complete

SYSTEM = (
    "You are a careful, empathetic medical assistant for clinicians and patients. "
    "Answer using ONLY the provided context (notes and imaging findings) and general medical knowledge. "
    "Do not give definitive diagnoses or treatment instructions; suggest discussing with a clinician. "
    "If information is missing, say so briefly. Keep answers concise and clear."
)

DISCLAIMER = (
    "\n\n_I’m an AI assistant, not a doctor. This is general information and not medical advice. "
    "For urgent concerns, seek immediate care._"
)

def answer(message: str, notes: str | None = None, imaging_findings: list[str] | None = None) -> str:
    ctx_parts = []
    if notes:
        ctx_parts.append(f"Clinical notes:\n{notes.strip()[:5000]}")
    if imaging_findings:
        joined = "\n".join(f"- {f}" for f in imaging_findings[:20])
        ctx_parts.append(f"Imaging findings:\n{joined}")
    ctx = "\n\n".join(ctx_parts) if ctx_parts else "(no case context provided)"

    user = (
        f"Context for this case:\n{ctx}\n\n"
        f"User question: {message}\n\n"
        "Answer directly, referencing the context where possible. "
        "If probabilities are mentioned in imaging, keep them as probabilities."
    )
    out = chat_complete(SYSTEM, user, temperature=0.3)
    return out + DISCLAIMER
