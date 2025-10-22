from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from backend.app.core.config import settings

def add_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
