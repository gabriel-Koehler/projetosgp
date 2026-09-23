"""Autenticação do professor e proteção das rotas administrativas (RF01, RNF06)."""

import secrets
from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status

from app.core import passwords
from app.core.config import Settings
from app.repositories.cadastros_repository import ProfessorRepository

SESSION_KEY = "professor"


@lru_cache
def _hash_falso() -> str:
    # Quando o usuário não existe, a verificação roda do mesmo jeito contra
    # este hash, para o tempo de resposta não revelar quais usuários existem.
    return passwords.gerar_hash(secrets.token_hex(8))


def verificar_credenciais(settings: Settings, username: str, password: str) -> bool:
    # compare_digest evita vazar, pelo tempo de resposta, quantos caracteres conferem.
    usuario_ok = secrets.compare_digest(username.encode(), settings.professor_username.encode())
    senha_ok = secrets.compare_digest(password.encode(), settings.professor_password.encode())
    return usuario_ok and senha_ok


def autenticar(request: Request, settings: Settings, username: str, password: str) -> dict | None:
    """Confere usuário e senha. Devolve os dados que vão para a sessão, ou None.

    Com banco configurado, usa a tabela professor (senha em hash). Sem banco
    (desenvolvimento), usa PROFESSOR_USERNAME / PROFESSOR_PASSWORD do .env.
    """
    pool = getattr(request.app.state, "pool", None)
    if pool is None:
        if not verificar_credenciais(settings, username, password):
            return None
        return {"id": None, "username": settings.professor_username, "nome": settings.professor_nome}

    with pool.connection() as conn:
        professor = ProfessorRepository(conn).obter_por_username(username)
    if not passwords.verificar(password, professor.senha_hash if professor else _hash_falso()) or not professor:
        return None
    return {"id": professor.id, "username": professor.username, "nome": professor.nome}


def require_professor(request: Request) -> dict:
    """Dependência que bloqueia a rota para quem não estiver logado.

    Uso: `APIRouter(dependencies=[Depends(require_professor)])` ou
    `professor: dict = Depends(require_professor)` na própria rota.
    """
    professor = request.session.get(SESSION_KEY)
    if not professor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Faça login para acessar esta área.",
        )
    return professor


def professor_id(professor: dict = Depends(require_professor)) -> int:
    """Id do professor logado, para filtrar os dados dele no banco."""
    if professor.get("id") is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados não configurado (DATABASE_URL).",
        )
    return professor["id"]
