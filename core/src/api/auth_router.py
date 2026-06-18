from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from src.dependencies import get_auth_service
from src.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Schemas ─────────────────────────────────────────────

class LoginBody(BaseModel):
    email: str
    password: str

class RegisterBody(BaseModel):
    email: str
    password: str
    nombre: str
    estilo_preferido: str

# ── Endpoints ───────────────────────────────────────────

@router.post("/login")
def login(body: LoginBody, service: AuthService = Depends(get_auth_service)):
    return service.login(body.email, body.password)


@router.post("/register")
def register(body: RegisterBody, service: AuthService = Depends(get_auth_service)):
    return service.register(body.email, body.password, body.nombre, body.estilo_preferido)


@router.get("/me")
def me(authorization: str = Header(), service: AuthService = Depends(get_auth_service)):
    token = authorization.removeprefix("Bearer ")
    return service.validar_sesion(token)


@router.post("/logout")
def logout(authorization: str = Header(), service: AuthService = Depends(get_auth_service)):
    token = authorization.removeprefix("Bearer ")
    service.logout(token)
    return {"ok": True}
