from backend.app.core.config import settings  # read from Pydantic .env

PROVIDER = (settings.llm_provider or "openai").lower()

_openai_client = None
_nim_session = None
_base_url = None

def _init_openai():
    from openai import OpenAI  # pip install openai
    api_key = settings.openai_api_key
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing in .env")
    return OpenAI(api_key=api_key)

def _init_nim():
    import os, requests
    api_key = os.getenv("NIM_API_KEY")
    base = os.getenv("NIM_API_BASE")
    if not api_key or not base:
        raise RuntimeError("NIM_API_KEY/NIM_API_BASE missing in .env")
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    return s, base.rstrip("/")

def chat_complete(system: str, user: str, temperature: float = 0.2) -> str:
    global _openai_client, _nim_session, _base_url

    if PROVIDER == "openai":
        if _openai_client is None:
            _openai_client = _init_openai()
        model = settings.openai_model or "gpt-4o-mini"
        resp = _openai_client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()

    if PROVIDER == "nim":
        import os
        if _nim_session is None:
            _nim_session, _base_url = _init_nim()
        url = f"{_base_url}/v1/chat/completions"
        model = os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct")
        payload = {
            "model": model,
            "messages": [{"role":"system","content":system},{"role":"user","content":user}],
            "temperature": temperature,
        }
        r = _nim_session.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()

    return "(LLM disabled) " + user[:200]
