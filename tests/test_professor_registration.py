import hashlib
import unittest
from contextlib import nullcontext
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi.testclient import TestClient

from app.core import passwords
from app.core.config import Settings
from app.database.connection import get_conn
from app.models.cadastros import Professor
from app.persistent import create_app


class ProfessorRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Settings(
            secret_key="test-secret",
            resend_api_key="test-key",
            registration_email_from="cadastro@example.com",
            google_client_id="test-client",
            google_client_secret="test-client-secret",
            google_redirect_uri="http://localhost/api/auth/google/callback",
        ))
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_registration_requires_email_code_and_only_then_starts_session(self):
        conn = Mock()
        conn.transaction.return_value = nullcontext()
        self.app.dependency_overrides[get_conn] = lambda: conn
        with (
            patch("app.controllers.auth.ProfessorRepository") as factory,
            patch("app.controllers.auth.registration_email.enviar_codigo") as send,
        ):
            repo = factory.return_value
            data = {
                "username": "Prof.Ana", "name": " Ana ", "email": "ANA@example.com",
                "password": "senha-forte", "passwordConfirmation": "senha-forte",
            }
            response = self.client.post("/api/auth/register", json=dict(data, email="invalido"))
            self.assertEqual(response.status_code, 422)
            mismatch = self.client.post("/api/auth/register", json=dict(data, passwordConfirmation="diferente"))
            self.assertEqual(mismatch.status_code, 422)
            repo.salvar_cadastro_pendente.assert_not_called()

            response = self.client.post("/api/auth/register", json=data)
            self.assertEqual(response.status_code, 202)
            self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
            repo.cadastrar.assert_not_called()

            _, recipient, code = send.call_args.args
            email, username, name, password_hash, code_hash = repo.salvar_cadastro_pendente.call_args.args
            self.assertEqual((recipient, email, username, name), ("ana@example.com", "ana@example.com", "prof.ana", "Ana"))
            self.assertTrue(passwords.verificar(data["password"], password_hash))
            self.assertEqual(code_hash, hashlib.sha256(code.encode()).hexdigest())
            self.assertNotIn(code, response.text)

            pending = {"email": email, "username": username, "nome": name, "senha_hash": password_hash}
            repo.consumir_cadastro_pendente.side_effect = [None, pending, None]
            repo.cadastrar.return_value = {"id": 42, "username": username, "nome": name}
            invalid = self.client.post("/api/auth/confirm-email", json={"email": email, "code": "A" * 16})
            self.assertEqual(invalid.status_code, 400)
            repo.cadastrar.assert_not_called()

            confirmed = self.client.post("/api/auth/confirm-email", json={"email": email, "code": code})
            self.assertEqual(confirmed.status_code, 201)
            repo.consumir_cadastro_pendente.assert_called_with(email, code_hash)
            repo.cadastrar.assert_called_once_with(**pending)
            self.assertEqual(self.client.get("/api/auth/me").json(), confirmed.json())

            self.assertEqual(self.client.post("/api/auth/confirm-email", json={"email": email, "code": code}).status_code, 400)
            repo.cadastro_disponivel.return_value = False
            self.assertEqual(self.client.post("/api/auth/register", json=data).status_code, 409)
            send.assert_called_once()

    def test_delivery_failure_removes_pending_registration(self):
        self.app.dependency_overrides[get_conn] = lambda: Mock()
        with (
            patch("app.controllers.auth.ProfessorRepository") as factory,
            patch("app.controllers.auth.registration_email.enviar_codigo", side_effect=httpx.ConnectError("offline")),
        ):
            response = self.client.post("/api/auth/register", json={
                "username": "prof.ana", "name": "Ana", "email": "ana@example.com",
                "password": "senha-forte", "passwordConfirmation": "senha-forte",
            })
            self.assertEqual(response.status_code, 503)
            repository = factory.return_value
            repository.cancelar_cadastro_pendente.assert_called_once_with(
                "ana@example.com", repository.salvar_cadastro_pendente.call_args.args[-1]
            )
            self.assertEqual(self.client.get("/api/auth/me").status_code, 401)

    def test_password_login_accepts_username_and_email(self):
        account = Professor(42, "prof.ana", "Ana", passwords.gerar_hash("senha-forte", 1000))
        with (
            patch("app.core.security.obter_pool") as pool,
            patch("app.core.security.ProfessorRepository") as factory,
        ):
            pool.return_value.connection.return_value = nullcontext(Mock())
            repo = factory.return_value
            repo.obter_por_username.side_effect = lambda identifier: account if identifier == "prof.ana" else None
            repo.obter_por_email.side_effect = lambda email: account if email == "ana@example.com" else None
            for identifier in ("PROF.ANA", "ANA@example.com"):
                with self.subTest(identifier=identifier):
                    response = self.client.post("/api/auth/login", json={
                        "username": identifier, "password": "senha-forte",
                    })
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()["username"], "prof.ana")

    def test_google_rejects_invalid_state_and_starts_professor_session(self):
        start = self.client.get("/api/auth/google", follow_redirects=False)
        destination = urlsplit(start.headers["location"])
        self.assertEqual((destination.scheme, destination.netloc), ("https", "accounts.google.com"))
        query = parse_qs(destination.query)
        self.assertEqual(query["code_challenge_method"], ["S256"])
        callback = "/api/auth/google/callback"
        with (
            patch("app.controllers.auth.google_auth.fetch_profile", return_value=("subject-1", "Ana")) as profile,
            patch("app.controllers.auth.obter_pool") as pool,
            patch("app.controllers.auth.ProfessorRepository") as factory,
        ):
            pool.return_value.connection.return_value = nullcontext(Mock())
            repo = factory.return_value
            repo.autenticar_google.return_value = {"id": 42, "username": "google-teste", "nome": "Ana"}
            params = {"state": "incorreto", "code": "codigo"}
            response = self.client.get(callback, params=params, follow_redirects=False)
            self.assertEqual(response.headers["location"], "/?google=failed")
            profile.assert_not_called()

            params["state"] = query["state"][0]
            response = self.client.get(callback, params=params, follow_redirects=False)
            self.assertEqual(response.headers["location"], "/dashboard")
            repo.autenticar_google.assert_called_once_with("subject-1", "Ana")
            self.assertEqual(self.client.get("/api/auth/me").json()["nome"], "Ana")
            response = self.client.get(callback, params=params, follow_redirects=False)
            self.assertEqual(response.headers["location"], "/?google=failed")
            profile.assert_called_once()

    def test_google_without_configuration(self):
        with TestClient(create_app(Settings(secret_key="test-secret"))) as client:
            response = client.get("/api/auth/google", follow_redirects=False)
            self.assertEqual(response.headers["location"], "/?google=unavailable")
