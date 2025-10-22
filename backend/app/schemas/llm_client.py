import os
from typing import List, Dict, Optional

PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

# --- OpenAI ---
_openai_client = None
if PROVIDER == "openai":
    from openai import OpenAI
    _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- NVIDIA NIM (optional) ---
_nim_session = None
if PROVIDER == "nim":
    import requests
    NIM_API_BASE = os.getenv("NIM_API_BASE")  # e.g. https://integrate.api.nvidia.com
    NIM_API_KEY = os.getenv("NIM_API_KEY")
    _nim_session = requests.Session()
    _nim_session.headers.update({"Authorization": f"Bearer {NIM_API_KEY}", "Content-Type": "application/json"})

def chat_complete(system: str, user: str, temperature: float = 0.2) -> str:
    """
    Simple helper for a single-turn system+user → assistant string.
    """
    if PROVIDER == "openai":
        resp = _openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

    elif PROVIDER == "nim":
        import json
        url = f"{os.getenv('NIM_API_BASE').rstrip('/')}/v1/chat/completions"
        payload = {
            "model": os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        r = _nim_session.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    else:
        # local/offline placeholder
        return "(LLM disabled) " + user[:200]
