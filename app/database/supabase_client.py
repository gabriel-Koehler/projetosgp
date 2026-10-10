"""Cliente do Supabase (supabase-py), usado para o Storage das fotos das folhas de resposta.

Os dados (tabelas) são acessados direto pelo PostgreSQL (DATABASE_URL), porque a
API REST do Supabase não faz transações com vários comandos (necessário no [N2-BE-04]).
"""

import logging
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import Settings, get_settings


def criar_cliente_supabase(settings: Settings) -> Client | None:
    if not (settings.supabase_url and settings.supabase_key):
        return None
    return create_client(settings.supabase_url, settings.supabase_key)


@lru_cache
def _cliente_padrao() -> Client | None:
    return criar_cliente_supabase(get_settings())


def get_supabase() -> Client | None:
    return _cliente_padrao()


def salvar_foto(cliente: Client | None, bucket: str, caminho: str, conteudo: bytes, tipo: str) -> str | None:
    """Guarda a foto da folha no Storage. Falha no upload não impede a correção: só não guarda a foto."""
    if cliente is None:
        return None
    try:
        cliente.storage.from_(bucket).upload(caminho, conteudo, {"content-type": tipo})
    except Exception:  # noqa: BLE001 - o resultado vale mais que a foto
        logging.getLogger(__name__).exception("Falha ao enviar a foto %s para o Storage", caminho)
        return None
    return f"{bucket}/{caminho}"
