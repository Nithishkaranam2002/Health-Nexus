from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.core.security import create_access_token

router = APIRouter()

class LoginIn(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=1)  # demo only
    role: str = Field(..., pattern="^(clinician|patient|admin)$")

@router.post("/auth/login")
def login(in_: LoginIn):
    # DEMO ONLY: accept any username if password == "demo"
    if in_.password != "demo":
        raise HTTPException(status_code=401, detail="Invalid credentials (demo expects password='demo')")
    token = create_access_token(sub=in_.username, role=in_.role)
    return {"access_token": token, "token_type": "bearer", "role": in_.role, "user": in_.username}
