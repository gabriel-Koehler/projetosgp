"""A API em camadas montada em /n1 dentro do app do MVP (app/main.py), como roda em produção."""

from dataclasses import replace

from fastapi.testclient import TestClient
from test_avaliacoes_qrcode import ler_qrcode, payload

from app.core.config import get_settings
from app.main import app


def test_mounted_backend_preserves_mvp_and_public_qr_contract(settings, banco, banco_url):
    backend = next(route.app for route in app.routes if getattr(route, "path", None) == "/n1")
    previous = backend.dependency_overrides.copy()
    backend.dependency_overrides[get_settings] = lambda: replace(settings, database_url=banco_url)
    try:
        with TestClient(app) as client:
            # O contrato do MVP (front da N1) continua igual.
            assert client.post("/api/auth/login", json={"email": "professor", "password": "123456"}).status_code == 200
            assert client.get("/api/questoes").status_code == 200

            assert client.get("/n1/api/painel").status_code == 401
            login = client.post("/n1/api/auth/login", json={"username": "professor", "password": "senha-teste"})
            assert login.status_code == 200
            ids = [
                client.post(
                    "/n1/api/questoes",
                    json={"enunciado": f"Q{i}", "alternativas": ["a", "b", "c", "d"], "correta": "A"},
                ).json()["id"]
                for i in range(3)
            ]
            response = client.post("/n1/api/avaliacoes", json=payload(ids))
            assert response.status_code == 201
            evaluation = response.json()
            version = evaluation["versoes"][0]
            assert version["url_qrcode"].startswith("/n1/api/avaliacoes/")
            # O QR Code abre a página do aluno no front; ela consulta a API pública.
            assert version["url_aluno"] == f"http://testserver/student?token={version['codigo']}"
            assert ler_qrcode(client.get(version["url_qrcode"]).content) == version["url_aluno"]
            publica = f"/n1/api/public/gabaritos/{version['codigo']}"
            with TestClient(app) as anonymous:
                assert anonymous.get(publica).status_code == 403
                liberar = client.patch(f"/n1/api/avaliacoes/{evaluation['id']}/gabarito", json={"liberado": True})
                assert liberar.status_code == 200
                assert set(anonymous.get(publica).json()) == {"avaliacao", "versao", "gabarito"}
            assert client.post("/n1/api/auth/logout").status_code == 204
            assert client.get("/n1/api/painel").status_code == 401
            assert client.get("/api/questoes").status_code == 200
    finally:
        backend.dependency_overrides = previous
        pool = getattr(backend.state, "pool", None)
        if pool is not None:  # o pool aponta para o banco de teste: fecha para não vazar entre testes
            pool.close()
            backend.state.pool = None
