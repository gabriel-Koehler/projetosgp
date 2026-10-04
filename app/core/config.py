"""Configurações da aplicação lidas das variáveis de ambiente."""

import os
import secrets
import warnings
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import load_dotenv


def _bool(valor: str | None, padrao: bool = False) -> bool:
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "sim", "yes"}


def _lista(valor: str | None) -> list[str]:
    return [item.strip() for item in (valor or "").split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    secret_key: str
    professor_username: str = "professor"
    professor_password: str = "123456"
    professor_nome: str = "Professor"
    session_https_only: bool = False
    session_max_age: int = 60 * 60 * 8
    cors_origins: list[str] = field(default_factory=list)
    # URL pública usada no QR Code. Vazio = endereço de quem fez a requisição.
    public_base_url: str | None = None
    # PostgreSQL do Supabase (Project Settings > Database > Connection string).
    database_url: str | None = None
    # Supabase Storage para as fotos das folhas (opcional).
    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_bucket: str = "folhas-resposta"


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        # Sem chave fixa, as sessões expiram a cada reinício do servidor.
        warnings.warn("SECRET_KEY não definida; usando chave temporária.", stacklevel=2)
        secret_key = secrets.token_urlsafe(32)

    return Settings(
        secret_key=secret_key,
        professor_username=os.getenv("PROFESSOR_USERNAME", "professor"),
        professor_password=os.getenv("PROFESSOR_PASSWORD", "123456"),
        professor_nome=os.getenv("PROFESSOR_NOME", "Professor"),
        session_https_only=_bool(os.getenv("SESSION_HTTPS_ONLY")),
        cors_origins=_lista(os.getenv("CORS_ORIGINS")),
        public_base_url=os.getenv("PUBLIC_BASE_URL") or None,
        database_url=os.getenv("DATABASE_URL") or None,
        supabase_url=os.getenv("SUPABASE_URL") or None,
        supabase_key=os.getenv("SUPABASE_KEY") or None,
        supabase_bucket=os.getenv("SUPABASE_BUCKET", "folhas-resposta"),
    )
