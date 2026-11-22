"""Cadastro e autenticação do professor."""

import httpx
import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from psycopg_pool import PoolTimeout

from app.core import google_auth, passwords
from app.core.config import Settings, get_settings
from app.core.security import SESSION_KEY, autenticar, require_professor
from app.database.connection import get_conn, obter_pool
from app.repositories.cadastros_repository import ProfessorRepository
from app.schemas.auth import LoginRequest, ProfessorResponse, RegisterRequest

router = APIRouter(prefix="/api/auth", tags=["autenticação"])


def iniciar_sessao(request: Request, professor: dict) -> dict:
    request.session.clear()
    request.session[SESSION_KEY] = professor
    return professor


@router.post("/login", response_model=ProfessorResponse)
def login(dados: LoginRequest, request: Request, settings: Settings = Depends(get_settings)):
    professor = autenticar(request, settings, dados.username, dados.password)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
        )

    return iniciar_sessao(request, professor)


@router.post("/register", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def register(dados: RegisterRequest, request: Request, conn: psycopg.Connection = Depends(get_conn)):
    professor = ProfessorRepository(conn).cadastrar(
        dados.email.lower(), dados.name, passwords.gerar_hash(dados.password)
    )
    if professor is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma conta com esse e-mail.")
    return iniciar_sessao(request, professor)


@router.get("/options")
def options(settings: Settings = Depends(get_settings)):
    return {"google": settings.google_enabled}


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303, headers={
        "Cache-Control": "no-store",
        "Referrer-Policy": "no-referrer",
    })


@router.get("/google")
def google_start(request: Request, settings: Settings = Depends(get_settings)):
    if not settings.google_enabled:
        return redirect("/?google=unavailable")
    return redirect(google_auth.authorization_url(request, settings))


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    settings: Settings = Depends(get_settings),
):
    if not settings.google_enabled:
        return redirect("/?google=unavailable")
    verifier = google_auth.consume_verifier(request, state)
    if not verifier or not code:
        return redirect("/?google=failed")
    try:
        profile = google_auth.fetch_profile(settings, code, verifier)
        if not profile:
            return redirect("/?google=failed")
        pool = obter_pool(request.app, settings)
        if pool is None:
            return redirect("/?google=unavailable")
        with pool.connection() as conn:
            professor = ProfessorRepository(conn).autenticar_google(*profile)
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError,
            psycopg.OperationalError, PoolTimeout):
        return redirect("/?google=failed")
    iniciar_sessao(request, professor)
    return redirect("/dashboard")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request):
    request.session.clear()


@router.get("/me", response_model=ProfessorResponse)
def me(professor: dict = Depends(require_professor)):
    return professor
