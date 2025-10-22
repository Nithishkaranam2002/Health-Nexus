from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.records import router as records_router
from backend.app.api.v1.images import router as images_router
from backend.app.api.v1.chat import router as chat_router

app = FastAPI(title="MedAssist-AI")

# CORS (adjust origins via env if you already have settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router,   prefix="/api/v1")
app.include_router(records_router, prefix="/api/v1")
app.include_router(images_router,  prefix="/api/v1")
app.include_router(chat_router,    prefix="/api/v1")


@app.get("/")
def root():
    return {"app": "MedAssist-AI", "status": "ok"}
