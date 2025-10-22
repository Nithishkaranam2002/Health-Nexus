from .llm_client import chat_complete

SYSTEM = (
    "You are a friendly medical explainer for patients. "
    "You provide general information only, avoid diagnosis, and always encourage professional care."
)

DISCLAIMER = (
    "\n\n_I’m an AI assistant, not a doctor. For emergencies, seek immediate care._"
)

def reply_to_patient(msg: str) -> str:
    out = chat_complete(SYSTEM, f"Answer simply and clearly:\n\n{msg}", temperature=0.4)
    return out + DISCLAIMER
