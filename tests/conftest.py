import os

os.environ.setdefault("SECRET_KEY", "chave-de-teste")

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.repositories.avaliacao_repository import AvaliacaoRepository, get_avaliacao_repository


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
