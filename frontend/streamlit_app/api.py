import os
import requests

API_BASE = os.getenv("STREAMLIT_API_BASE", "http://127.0.0.1:8001")


def _headers(token: str | None = None) -> dict:
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def login(username: str, password: str, role: str):
    r = requests.post(
        f"{API_BASE}/api/v1/auth/login",
        json={"username": username, "password": password, "role": role},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def get_health(token: str | None = None):
    r = requests.get(f"{API_BASE}/api/v1/health", headers=_headers(token), timeout=20)
    r.raise_for_status()
    return r.json()


def analyze_image(file_bytes: bytes, filename: str, token: str | None = None):
    files = {"file": (filename, file_bytes, "application/octet-stream")}
    r = requests.post(
        f"{API_BASE}/api/v1/images/analyze",
        files=files,
        headers=_headers(token),
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def extract_pdf_text(file_bytes: bytes, filename: str, token: str | None = None):
    files = {"file": (filename, file_bytes, "application/pdf")}
    r = requests.post(
        f"{API_BASE}/api/v1/records/extract_pdf",
        files=files,
        headers=_headers(token),
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def summarize_records(text: str, imaging_findings=None, token: str | None = None):
    payload = {"text": text, "imaging_findings": imaging_findings or []}
    r = requests.post(
        f"{API_BASE}/api/v1/records/summarize",
        json=payload,
        headers=_headers(token),
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def patient_chat(
    message: str,
    notes: str | None = None,
    imaging_findings=None,
    token: str | None = None,
):
    payload = {"message": message, "notes": notes, "imaging_findings": imaging_findings or []}
    r = requests.post(
        f"{API_BASE}/api/v1/chat",
        json=payload,
        headers=_headers(token),
        timeout=90,
    )
    r.raise_for_status()
    return r.json()
