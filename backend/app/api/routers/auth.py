from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, EmailStr
from app.db import repo

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str  # "doctor" | "assistant"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(body: RegisterIn):
    if body.role not in ("doctor", "assistant"):
        raise HTTPException(400, "Invalid role")
    if repo.get_user_by_email(body.email):
        raise HTTPException(400, "Email already registered")
    user_id = repo.create_user(
        body.email, body.full_name, body.password, body.role)
    session_id, expires = repo.create_session(user_id)
    return {"session_id": session_id, "role": body.role, "expires_at": str(expires)}


@router.post("/login")
def login(body: LoginIn):
    u = repo.check_password(body.email, body.password)
    if not u:
        raise HTTPException(401, "Invalid credentials")
    session_id, expires = repo.create_session(u["id"])
    return {"session_id": session_id, "role": u["role"], "expires_at": str(expires)}


@router.get("/me")
def me(x_session_id: str):
    s = repo.get_session(x_session_id)
    if not s:
        raise HTTPException(401, "Invalid session")
    return {"email": s["email"], "full_name": s["full_name"], "role": s["role"]}


@router.post("/logout")
def logout(x_session_id: str = Body(..., embed=True)):
    repo.delete_session(x_session_id)
    return {"ok": True}
