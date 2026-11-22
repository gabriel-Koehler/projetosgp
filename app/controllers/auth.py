"""Cadastro e autenticação do professor."""

import hashlib
import secrets

import httpx
import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from psycopg_pool import PoolTimeout

from app.core import google_auth, passwords, registration_email
from app.core.config import Settings, get_settings
from app.core.security import SESSION_KEY, autenticar, require_professor
from app.database.connection import get_conn, obter_pool
from app.repositories.cadastros_repository import ProfessorRepository
from app.schemas.auth import ConfirmEmailRequest, LoginRequest, ProfessorResponse, RegisterRequest

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


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
def register(
    dados: RegisterRequest,
    conn: psycopg.Connection = Depends(get_conn),
    settings: Settings = Depends(get_settings),
):
    if dados.password != dados.passwordConfirmation:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "As senhas não coincidem.")
    if not settings.resend_api_key or not settings.registration_email_from:
        raise HTTPException(503, "O envio de códigos de confirmação está indisponível.")
    email, username = dados.email.lower(), dados.username.lower()
    repository = ProfessorRepository(conn)
    if not repository.cadastro_disponivel(username, email):
        raise HTTPException(409, "Nome de usuário ou e-mail já cadastrado.")
    codigo = secrets.token_urlsafe(12)
    codigo_hash = hashlib.sha256(codigo.encode()).hexdigest()
    if not repository.salvar_cadastro_pendente(
        email, username, dados.name, passwords.gerar_hash(dados.password), codigo_hash
    ):
        raise HTTPException(429, "Aguarde um minuto antes de solicitar outro código.")
    try:
        registration_email.enviar_codigo(settings, email, codigo)
    except httpx.HTTPError as error:
        repository.cancelar_cadastro_pendente(email, codigo_hash)
        raise HTTPException(503, "Não foi possível enviar o código. Confira o e-mail e tente novamente.") from error
    return {"message": "Enviamos um código para o seu e-mail. Ele vale por 15 minutos."}


@router.post("/confirm-email", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def confirm_email(dados: ConfirmEmailRequest, request: Request, conn: psycopg.Connection = Depends(get_conn)):
    repository = ProfessorRepository(conn)
    codigo_hash = hashlib.sha256(dados.code.encode()).hexdigest()
    with conn.transaction():
        cadastro = repository.consumir_cadastro_pendente(dados.email.lower(), codigo_hash)
        if cadastro is None:
            raise HTTPException(400, "Código inválido ou expirado. Confira o código ou solicite outro.")
        professor = repository.cadastrar(**cadastro)
    if professor is None:
        raise HTTPException(409, "Nome de usuário ou e-mail já cadastrado.")
    return iniciar_sessao(request, professor)


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
