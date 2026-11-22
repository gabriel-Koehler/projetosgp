from fastapi.testclient import TestClient

from app.core.config import Settings
from app.persistent import create_app
from app.repositories.cadastros_repository import ProfessorRepository


def test_register_persists_only_after_email_verification(banco, banco_url, monkeypatch):
    sent = {}
    monkeypatch.setattr(
        "app.controllers.auth.registration_email.enviar_codigo",
        lambda _settings, email, code: sent.update({email: code}),
    )
    app = create_app(Settings(
        secret_key="teste", database_url=banco_url,
        resend_api_key="teste", registration_email_from="cadastro@example.com",
    ))
    data = {
        "name": "Ana", "username": "prof.ana", "email": "Ana@example.com",
        "password": "senha-forte", "passwordConfirmation": "senha-forte",
    }
    with TestClient(app) as api:
        assert api.post("/api/auth/register", json=data).status_code == 202
        assert api.post("/api/auth/register", json=data).status_code == 429
        assert api.get("/api/auth/me").status_code == 401
        login = {"username": "prof.ana", "password": data["password"]}
        assert api.post("/api/auth/login", json=login).status_code == 401

        confirmation = {"email": data["email"], "code": sent["ana@example.com"]}
        assert api.post("/api/auth/confirm-email", json=confirmation).status_code == 201
        assert api.post("/api/auth/confirm-email", json=confirmation).status_code == 400
        assert api.post("/api/auth/logout").status_code == 204
        for identifier in ("ANA@example.com", "Prof.Ana"):
            response = api.post("/api/auth/login", json=dict(login, username=identifier))
            assert response.json() == {"username": "prof.ana", "nome": "Ana"}
        assert api.post("/api/auth/register", json=data).status_code == 409
        assert api.get("/api/semestres").json() == []


def test_google_subject_reuses_professor_and_preserves_local_account(banco):
    repo = ProfessorRepository(banco)
    local = repo.cadastrar("prof.ana", "ana@example.com", "Ana", "hash")
    google = repo.autenticar_google("subject-123", "Ana")

    assert local["id"] != google["id"]
    assert repo.autenticar_google("subject-123", "Nome atualizado")["id"] == google["id"]
    assert repo.obter_por_username(google["username"]).senha_hash is None
