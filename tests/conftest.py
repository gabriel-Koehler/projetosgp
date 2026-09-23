import os

os.environ.setdefault("SECRET_KEY", "chave-de-teste")

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.database import migrate
from app.database.connection import conectar
from app.main import create_app
from app.repositories.avaliacao_repository import AvaliacaoRepository, get_avaliacao_repository

# Testes que usam o banco rodam só com TEST_DATABASE_URL definida (um banco
# PostgreSQL descartável: as tabelas são apagadas e recriadas).
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture
def settings() -> Settings:
    return Settings(
        secret_key="chave-de-teste",
        professor_username="professor",
        professor_password="senha-teste",
        professor_nome="Prof. Teste",
    )


@pytest.fixture
def client(settings) -> TestClient:
    app = create_app(settings)
    repositorio = AvaliacaoRepository()  # estado limpo a cada teste
    app.dependency_overrides[get_avaliacao_repository] = lambda: repositorio
    return TestClient(app)


@pytest.fixture
def client_logado(client) -> TestClient:
    resposta = client.post("/api/auth/login", json={"username": "professor", "password": "senha-teste"})
    assert resposta.status_code == 200
    return client


# --- Banco de dados -------------------------------------------------------------


@pytest.fixture(scope="session")
def banco_url():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL não definida")
    with conectar(TEST_DATABASE_URL) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
        migrate.aplicar_schema(conn)
    return TEST_DATABASE_URL


@pytest.fixture
def banco(banco_url, settings):
    """Conexão com as tabelas vazias e o professor de teste criado."""
    with conectar(banco_url) as conn:
        tabelas = conn.execute(
            "SELECT string_agg(quote_ident(tablename), ', ') AS t FROM pg_tables WHERE schemaname = 'public'"
        ).fetchone()["t"]
        conn.execute(f"TRUNCATE {tabelas} RESTART IDENTITY CASCADE")
        migrate.garantir_professor(conn, settings, iteracoes=1000)  # hash rápido nos testes
        yield conn


@pytest.fixture
def api(banco, banco_url, settings):
    """Cliente da API ligado ao banco de teste, com o professor logado."""
    from dataclasses import replace

    app = create_app(replace(settings, database_url=banco_url))
    with TestClient(app) as cliente:
        resposta = cliente.post("/api/auth/login", json={"username": "professor", "password": "senha-teste"})
        assert resposta.status_code == 200
        yield cliente
