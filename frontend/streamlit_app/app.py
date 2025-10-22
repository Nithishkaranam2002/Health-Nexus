import os
import streamlit as st
import pandas as pd

from api import (
    login,
    get_health,
    summarize_records,
    patient_chat,
    analyze_image,
    extract_pdf_text,
)

# -------------------------------------------------------------------
# App config
# -------------------------------------------------------------------
st.set_page_config(page_title="MedAssist-AI", page_icon="🩺", layout="centered")
API_BASE = os.getenv("STREAMLIT_API_BASE", "http://127.0.0.1:8001")


def do_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:  # fallback for older Streamlit
        st.experimental_rerun()


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def pct(p):
    try:
        return f"{float(p) * 100:.0f}%"
    except Exception:
        return "—"


def render_image_result(res: dict, role: str = "clinician"):
    """
    Render imaging results in role-aware fashion:
      - Patient: plain-English summary only
      - Clinician/Admin: summary + ranked table + raw JSON
    """
    st.success("Image analysis complete")

    modality = res.get("modality", "image")
    shape = res.get("shape", [])
    top5 = res.get("top5", [])  # e.g. [{"label":"Effusion","prob":0.66}, ...]

    # --- Plain-English summary ---
    st.markdown("### Findings (summary)")
    if top5:
        primary = top5[0]
        dims = (
            f"{shape[0]}×{shape[1]}"
            if isinstance(shape, (list, tuple)) and len(shape) == 2
            else "n/a"
        )
        lines = [
            f"- **Modality:** {modality}",
            f"- **Image size:** {dims}",
            f"- **Most likely finding:** **{primary.get('label','—')}** ({pct(primary.get('prob', 0))})",
        ]
        if len(top5) > 1 and role != "patient":
            others = ", ".join(
                f"{x.get('label','—')} ({pct(x.get('prob',0))})" for x in top5[1:3]
            )
            lines.append(f"- **Other possibilities:** {others}")
        st.write("\n".join(lines))
    else:
        st.info("No prominent findings detected.")

    # Patient sees only the summary
    if role == "patient":
        st.caption(
            "Note: This is AI assistance and may be imperfect. Please follow your clinician’s guidance."
        )
        return

    # --- Clinician/Admin: ranked table ---
    if top5:
        df = pd.DataFrame(top5)
        if "prob" in df.columns:
            df["Probability"] = (df["prob"].astype(float) * 100).map(
                lambda x: f"{x:.1f}%"
            )
            df = df.rename(columns={"label": "Finding"})[["Finding", "Probability"]]
        else:
            df = df.rename(columns={"label": "Finding"})
        st.markdown("#### Ranked findings")
        st.dataframe(df, use_container_width=True)

    # --- Raw JSON (collapsible) ---
    with st.expander("Raw JSON"):
        st.json(res)

    st.caption(
        "Note: AI output for review only—correlate with clinical context & radiologist read."
    )


# -------------------------------------------------------------------
# Auth state
# -------------------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = {"token": None, "user": None, "role": None}

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.title("MedAssist-AI")
    st.caption(f"Backend: {API_BASE}")

    if st.session_state.auth["token"]:
        st.success(
            f"Logged in as {st.session_state.auth['user']} ({st.session_state.auth['role']})"
        )
        if st.button("Logout"):
            st.session_state.auth = {"token": None, "user": None, "role": None}
            do_rerun()
    else:
        st.subheader("Login (demo)")
        username = st.text_input("Username", value="demo_user")
        password = st.text_input("Password", value="demo", type="password")
        role_choice = st.selectbox("Role", ["clinician", "patient", "admin"])
        if st.button("Login"):
            try:
                resp = login(username, password, role_choice)
                st.session_state.auth = {
                    "token": resp["access_token"],
                    "user": resp["user"],
                    "role": resp["role"],
                }
                do_rerun()
            except Exception as e:
                st.error(str(e))

    if st.button("Ping /health"):
        try:
            st.success(get_health(st.session_state.auth["token"]))
        except Exception as e:
            st.error(str(e))

# -------------------------------------------------------------------
# Routing by role
# -------------------------------------------------------------------
role = st.session_state.auth["role"]
st.title("MedAssist-AI")

if not role:
    st.info("Please log in to access the application.")
    st.stop()

# ===================================================================
# CLINICIAN / ADMIN
# ===================================================================
if role in ("clinician", "admin"):
    st.subheader("Summarize Clinical Notes + Imaging (MVP)")

    col1, col2 = st.columns(2)
    with col1:
        img_file = st.file_uploader(
            "Upload medical image (PNG/JPG/DICOM)",
            type=["png", "jpg", "jpeg", "dcm"],
            key="img_uploader",
        )
    with col2:
        pdf_file = st.file_uploader(
            "Upload clinical PDF (EHR/notes)", type=["pdf"], key="pdf_uploader"
        )

    findings: list[str] = st.session_state.get("last_findings", [])

    # Analyze image
    if img_file is not None and st.button("Analyze image"):
        with st.spinner("Analyzing image..."):
            try:
                res = analyze_image(
                    img_file.read(),
                    img_file.name,
                    token=st.session_state.auth["token"],
                )
                render_image_result(res, role=st.session_state.auth.get("role", "clinician"))
                findings = res.get("findings", [])
                st.session_state["last_findings"] = findings
            except Exception as e:
                st.error(str(e))

    st.caption("Paste de-identified notes or extract from PDF:")

    # Extract text from PDF
    if pdf_file is not None and st.button("Extract text from PDF"):
        with st.spinner("Extracting text..."):
            try:
                out = extract_pdf_text(
                    pdf_file.read(), pdf_file.name, token=st.session_state.auth["token"]
                )
                st.session_state["notes_text"] = out.get("text", "")
                st.success("Text extracted from PDF")
            except Exception as e:
                st.error(str(e))

    text = st.text_area(
        "Notes",
        height=220,
        placeholder="CC/HPI...\nMedications...\nLabs...",
        value=st.session_state.get("notes_text", ""),
    )

    # Summarize
    if st.button("Summarize"):
        if not text.strip() and not findings:
            st.warning("Provide notes and/or analyze an image.")
        else:
            with st.spinner("Summarizing..."):
                try:
                    out = summarize_records(
                        text, findings, token=st.session_state.auth["token"]
                    )
                    st.success("Summary")
                    st.write(out.get("summary", ""))
                    if out.get("citations"):
                        st.caption("Citations")
                        st.json(out["citations"])
                except Exception as e:
                    st.error(str(e))

    # Case-aware chat
    st.markdown("---")
    st.subheader("Ask AI about this case")

    case_notes = text
    case_findings = findings

    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = []

    for role_, msg in st.session_state.chat_msgs:
        st.chat_message("user" if role_ == "user" else "assistant").markdown(msg)

    cols = st.columns(3)
    sug1 = cols[0].button("Key problems?")
    sug2 = cols[1].button("What labs to monitor?")
    sug3 = cols[2].button("When to escalate?")

    chosen = None
    if sug1:
        chosen = "What are the key problems and differentials based on this case?"
    if sug2:
        chosen = "Which labs and vitals should be monitored over the next week, and why?"
    if sug3:
        chosen = "What red flags would warrant escalation or imaging follow-up?"

    prompt = st.chat_input("Ask a question about this case…")
    if chosen:
        prompt = chosen

    if prompt:
        st.session_state.chat_msgs.append(("user", prompt))
        with st.spinner("Thinking..."):
            try:
                resp = patient_chat(
                    prompt,
                    notes=case_notes,
                    imaging_findings=case_findings,
                    token=st.session_state.auth["token"],
                )
                bot = resp.get("reply", "")
                st.session_state.chat_msgs.append(("assistant", bot))
                st.chat_message("assistant").markdown(bot)
            except Exception as e:
                st.error(str(e))

# ===================================================================
# PATIENT
# ===================================================================
elif role == "patient":
    st.subheader("Ask a Question (with safety disclaimers)")

    st.markdown("**Upload your document (optional):**")
    doc = st.file_uploader(
        "Discharge summary, instructions, or notes", type=["pdf", "txt"], help="PDF or plain text."
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    use_context = c1.checkbox("Use document as context", value=True)
    extract_clicked = c2.button("Load / Extract")
    clear_clicked = c3.button("Clear")

    if "patient_context_text" not in st.session_state:
        st.session_state.patient_context_text = ""

    if clear_clicked:
        st.session_state.patient_context_text = ""

    if extract_clicked and doc is not None:
        try:
            if doc.name.lower().endswith(".pdf"):
                out = extract_pdf_text(doc.read(), doc.name, token=st.session_state.auth["token"])
                st.session_state.patient_context_text = out.get("text", "")
            else:
                st.session_state.patient_context_text = doc.read().decode(
                    "utf-8", errors="ignore"
                )
            st.success("Document loaded.")
        except Exception as e:
            st.error(f"Failed to load document: {e}")

    st.markdown("**Document context (editable, optional):**")
    st.session_state.patient_context_text = st.text_area(
        "Paste or review extracted text here",
        value=st.session_state.patient_context_text,
        height=180,
        placeholder="(Optional) Text from your document will appear here after upload.",
    )

    if "patient_chat" not in st.session_state:
        st.session_state.patient_chat = []

    for who, msg in st.session_state.patient_chat:
        st.chat_message("user" if who == "you" else "assistant").markdown(msg)

    prompt = st.chat_input("Type your question…")
    if prompt:
        st.session_state.patient_chat.append(("you", prompt))
        with st.spinner("Thinking..."):
            try:
                ctx = (
                    st.session_state.patient_context_text.strip()
                    if use_context and st.session_state.patient_context_text.strip()
                    else None
                )
                resp = patient_chat(prompt, notes=ctx, token=st.session_state.auth["token"])
                bot = resp.get("reply", "")
                st.session_state.patient_chat.append(("bot", bot))
                st.chat_message("assistant").markdown(bot)
            except Exception as e:
                st.error(str(e))

# ===================================================================
# ADMIN
# ===================================================================
else:
    st.subheader("Admin Console (MVP)")
    try:
        st.write("Health:", get_health(st.session_state.auth["token"]))
    except Exception as e:
        st.error(str(e))
