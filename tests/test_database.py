from dataclasses import replace

import psycopg
import pytest
from fastapi.testclient import TestClient

from app.core import passwords
from app.database import check, migrate
from app.main import create_app


def test_schema_cria_todas_as_tabelas(banco_url, settings):
    resultado = check.verificar_banco(replace(settings, database_url=banco_url))
    assert resultado["tabelas_faltando"] == []
    assert "PostgreSQL" in resultado["versao"]


def test_migracao_pode_rodar_de_novo(banco):
    migrate.aplicar_schema(banco)
    migrate.aplicar_schema(banco)


def test_professor_inicial_criado_uma_vez_com_senha_em_hash(banco, settings):
    assert migrate.garantir_professor(banco, settings) is False  # já criado pela fixture
    professor = banco.execute("SELECT * FROM professor").fetchone()

    assert professor["username"] == "professor"
    assert professor["senha_hash"] != "senha-teste"
    assert passwords.verificar("senha-teste", professor["senha_hash"])


def test_codigo_da_versao_e_unico(banco):
    banco.execute("INSERT INTO avaliacao (professor_id, nome, configuracao) VALUES (1, 'N1', '{}')")
    banco.execute("INSERT INTO versao_avaliacao (avaliacao_id, nome, codigo, ordem) VALUES (1, 'A', 'abc', 1)")
    with pytest.raises(psycopg.errors.UniqueViolation):
        banco.execute("INSERT INTO versao_avaliacao (avaliacao_id, nome, codigo, ordem) VALUES (1, 'B', 'abc', 2)")


def test_gabarito_nasce_bloqueado(banco):
    banco.execute("INSERT INTO avaliacao (professor_id, nome, configuracao) VALUES (1, 'N1', '{}')")
    assert banco.execute("SELECT gabarito_liberado FROM avaliacao").fetchone()["gabarito_liberado"] is False


def test_health_com_banco(settings, banco_url):
    with TestClient(create_app(replace(settings, database_url=banco_url))) as client:
        assert client.get("/api/health").json() == {"status": "ok", "banco": "ok"}


def test_health_sem_banco(client):
    assert client.get("/api/health").json() == {"status": "ok", "banco": "nao_configurado"}
