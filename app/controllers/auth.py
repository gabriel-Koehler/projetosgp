"""Rotas de login e logout do professor (RF01)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import Settings, get_settings
from app.core.security import SESSION_KEY, autenticar, require_professor
from app.schemas.auth import LoginRequest, ProfessorResponse

router = APIRouter(prefix="/api/auth", tags=["autenticação"])


@router.post("/login", response_model=ProfessorResponse)
def login(dados: LoginRequest, request: Request, settings: Settings = Depends(get_settings)):
    professor = autenticar(request, settings, dados.username, dados.password)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
        )

    request.session.clear()
    request.session[SESSION_KEY] = professor
    return professor


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()


@router.get("/me", response_model=ProfessorResponse)
def me(professor: dict = Depends(require_professor)):
    return professor
