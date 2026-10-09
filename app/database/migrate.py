"""Cria as tabelas e o professor inicial.

Uso: `python -m app.database.migrate` (lê DATABASE_URL e PROFESSOR_* do ambiente/.env).
Pode rodar várias vezes: o schema.sql é idempotente e o professor só é criado se não existir.
"""

from pathlib import Path

import psycopg

from app.core import passwords
from app.core.config import Settings, get_settings
from app.database.connection import conectar

SCHEMA = Path(__file__).with_name("schema.sql")


def aplicar_schema(conn: psycopg.Connection) -> None:
    with conn.transaction():
        conn.execute(SCHEMA.read_text(encoding="utf-8"))


def garantir_professor(conn: psycopg.Connection, settings: Settings, iteracoes: int = passwords.ITERACOES) -> bool:
    """Cria o professor configurado se ainda não existir. Retorna True se criou."""
    cursor = conn.execute(
        """
        INSERT INTO professor (username, nome, senha_hash)
        VALUES (%s, %s, %s)
        ON CONFLICT (username) DO NOTHING
        """,
        (
            settings.professor_username,
            settings.professor_nome,
            passwords.gerar_hash(settings.professor_password, iteracoes),
        ),
    )
    return cursor.rowcount == 1


def migrar(settings: Settings) -> None:
    if not settings.database_url:
        raise SystemExit("Defina DATABASE_URL no .env para rodar a migração.")
    with conectar(settings.database_url) as conn:
        aplicar_schema(conn)
        criado = garantir_professor(conn, settings)
    print("Tabelas criadas/atualizadas.")
    print(f"Professor '{settings.professor_username}': {'criado' if criado else 'já existia'}.")


if __name__ == "__main__":
    migrar(get_settings())
