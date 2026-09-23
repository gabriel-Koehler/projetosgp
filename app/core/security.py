"""Autenticação do professor e proteção das rotas administrativas (RF01, RNF06)."""

import secrets

from fastapi import HTTPException, Request, status

from app.core.config import Settings

SESSION_KEY = "professor"


def verificar_credenciais(settings: Settings, username: str, password: str) -> bool:
    # compare_digest evita vazar, pelo tempo de resposta, quantos caracteres conferem.
    usuario_ok = secrets.compare_digest(username.encode(), settings.professor_username.encode())
    senha_ok = secrets.compare_digest(password.encode(), settings.professor_password.encode())
    return usuario_ok and senha_ok


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
