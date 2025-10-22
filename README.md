# 🩺 MedAssist-AI  
### A Secure AI Assistant for Clinical Summarization, Imaging, and Patient Communication

---

## 🧭 Overview
**MedAssist-AI** is a privacy-preserving healthcare assistant built using **FastAPI**, **Streamlit**, and **LLM-based summarization and Q&A pipelines**.  
It enables doctors, patients, and administrators to interact with medical data safely — by summarizing records, analyzing medical images, and providing context-aware AI chat while ensuring **HIPAA/GDPR-aligned privacy**.

---

## 💡 What We Built
| Module | Description |
|--------|--------------|
| **Clinician Portal** | Upload patient notes (PDFs) and medical images. The backend extracts and summarizes EHRs using an LLM and provides a structured, citation-based summary. |
| **Patient Portal** | Patients can upload discharge summaries or visit notes and ask questions. The chatbot simplifies medical information into understandable language with disclaimers. |
| **Admin Console** | Displays system health, access logs, and verifies API uptime. |
| **Security Layer (RBAC)** | Role-Based Access Control ensures each user only sees what they are allowed to: clinicians view patient data; patients see only their own; admins monitor the system. |

---

## ⚙️ Architecture

Streamlit Frontend
├─ Role-based UI (Clinician / Patient / Admin)
├─ Auth login via FastAPI /auth
└─ Secure API calls → FastAPI backend
FastAPI Backend
├─ /auth → JWT issuance & login (RBAC)
├─ /records → PDF extraction + LLM summarization
├─ /images → Image analyzer (stub, MONAI-ready)
├─ /chat → Context-aware conversational LLM
├─ /core → Config, CORS, security
└─ /middleware → Audit logging (no PHI stored)


### 🔐 Security Model
- JWT Tokens → issued after login.  
- `require_role()` decorator → enforces access level.  
- PHI redaction before model calls.  
- Audit logs store *who accessed what*, not the actual data.  

---

## 🧰 Tech Stack
| Layer | Tools & Techniques |
|--------|--------------------|
| **Frontend** | Streamlit (Chat UI, Role-based Routing, Session State) |
| **Backend** | FastAPI, Pydantic v2, Async REST APIs |
| **Security** | PyJWT for authentication, RBAC for access control |
| **AI / NLP** | LLM summarization, contextual Q&A (OpenAI / NIM endpoint) |
| **Data Layer** | PDF text extraction, local embeddings, JSON metadata |
| **Compliance** | PHI redaction, disclaimers, audit logs (HIPAA-ready) |

---

## 🧠 Techniques Used
- **RAG Pattern (Prototype):** Summarization built to extend with Retrieval-Augmented Generation later.  
- **Role-Based UI:** Streamlit dynamically hides/show components based on JWT role.  
- **LLM-Oriented Summarization:** De-identified text → chunked embeddings → LLM for concise summaries.  
- **Guardrails & Disclaimers:** Every patient-facing response includes safety disclaimers.  
- **Modular Microservice Design:** Each module (chat, records, images) operates independently via `/api/v1/` endpoints.  

---

## 🔬 Real-World Scenarios Solved
1. **Clinician Documentation Overload:** Summarizes long EHR notes in seconds.  
2. **Patient Comprehension:** Simplifies complex medical terms into plain language.  
3. **Privacy Assurance:** All PHI is processed locally or stripped before leaving the system.  
4. **Audit & Compliance:** Tracks every access event for transparency.  

---

## 🧩 How to Run

### 1️⃣ Backend Setup
``bash
cd backend
uv run pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8001


cd streamlit_app
uv run streamlit run app.py --server.port 3000

Example Roles
 Clinician: Uploads notes/images → gets summarized report + AI insights.
 Patient: Uploads discharge doc → gets simplified answers via chatbot.
 Admin: Verifies system health & access logs.


 Future Improvements
Integrate MONAI for real medical image segmentation/classification.
Add RAG + Vector Store for multi-patient context retrieval.
Enable Offline Local-Llama Inference for complete privacy.
Expand Dashboard Analytics for hospital-scale monitoring.
