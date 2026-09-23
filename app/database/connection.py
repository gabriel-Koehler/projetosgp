"""Pool de conexões com o PostgreSQL do Supabase (DATABASE_URL).

Cada requisição pega uma conexão do pool. As conexões ficam em autocommit:
um comando isolado grava na hora, e operações com vários passos usam
`with conn.transaction():` no service (tudo ou nada).
"""

from collections.abc import Iterator

import psycopg
from fastapi import HTTPException, Request, status
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


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


def get_conn(request: Request) -> Iterator[psycopg.Connection]:
    pool: ConnectionPool | None = getattr(request.app.state, "pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados não configurado (DATABASE_URL).",
        )
    with pool.connection() as conn:
        yield conn
