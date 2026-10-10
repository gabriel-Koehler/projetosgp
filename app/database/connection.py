"""Pool de conexões com o PostgreSQL do Supabase (DATABASE_URL).

Cada requisição pega uma conexão do pool. As conexões ficam em autocommit:
um comando isolado grava na hora, e operações com vários passos usam
`with conn.transaction():` no service (tudo ou nada).
"""

from collections.abc import Iterator
from threading import Lock

import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request, status
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import Settings, get_settings

_lock = Lock()


def criar_pool(database_url: str, min_size: int = 1, max_size: int = 10) -> ConnectionPool:
    return ConnectionPool(
        database_url,
        min_size=min_size,
        max_size=max_size,
        open=True,
        kwargs={
            "autocommit": True,
            "row_factory": dict_row,
            # O pooler do Supabase (porta 6543, modo transaction) não aceita
            # prepared statements; desligar evita erros intermitentes.
            "prepare_threshold": None,
        },
    )


def conectar(database_url: str) -> psycopg.Connection:
    """Conexão avulsa (scripts de migração e teste de conectividade)."""
    return psycopg.connect(database_url, autocommit=True, row_factory=dict_row, prepare_threshold=None)


def obter_pool(app: FastAPI, settings: Settings) -> ConnectionPool | None:
    """Pool do app, aberto na primeira vez que for usado.

    Abrir aqui (e não só no lifespan) é necessário porque a API é montada em
    `/n1` dentro do app do MVP (app/main.py), e o Starlette não executa o
    lifespan de apps montados.
    """
    if getattr(app.state, "pool", None) is None and settings.database_url:
        with _lock:
            if getattr(app.state, "pool", None) is None:
                app.state.pool = criar_pool(settings.database_url)
    return getattr(app.state, "pool", None)


def get_conn(request: Request, settings: Settings = Depends(get_settings)) -> Iterator[psycopg.Connection]:
    pool = obter_pool(request.app, settings)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados não configurado (DATABASE_URL).",
        )
    with pool.connection() as conn:
        yield conn
