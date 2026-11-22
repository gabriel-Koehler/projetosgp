import unittest
from contextlib import nullcontext
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from app.core import passwords
from app.core.config import Settings
from app.database.connection import get_conn
from app.persistent import create_app


class ProfessorRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Settings(
            secret_key="test-secret",
            google_client_id="test-client",
            google_client_secret="test-client-secret",
            google_redirect_uri="http://localhost/api/auth/google/callback",
        ))
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_registration_validates_session_and_duplicate(self):
        self.app.dependency_overrides[get_conn] = lambda: Mock()
        with patch("app.controllers.auth.ProfessorRepository") as factory:
            repo = factory.return_value
            response = self.client.post("/api/auth/register", json={
                "name": " ", "email": "invalido", "password": "curta",
            })
            self.assertEqual(response.status_code, 422)
            repo.cadastrar.assert_not_called()
            repo.cadastrar.side_effect = [
                {"id": 42, "username": "ana@example.com", "nome": "Ana"}, None,
            ]
            data = {"name": " Ana ", "email": "ANA@example.com", "password": "senha-forte"}
            response = self.client.post("/api/auth/register", json=data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json(), {"username": "ana@example.com", "nome": "Ana"})
            email, name, password_hash = repo.cadastrar.call_args.args
            self.assertEqual((email, name), ("ana@example.com", "Ana"))
            self.assertTrue(passwords.verificar(data["password"], password_hash))
            self.assertEqual(self.client.get("/api/auth/me").json(), response.json())
            self.assertEqual(self.client.post("/api/auth/register", json=data).status_code, 409)

    def test_google_rejects_invalid_state_and_starts_professor_session(self):
        self.assertEqual(self.client.get("/api/auth/options").json(), {"google": True})
        start = self.client.get("/api/auth/google", follow_redirects=False)
        query = parse_qs(urlsplit(start.headers["location"]).query)
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
            self.assertEqual(client.get("/api/auth/options").json(), {"google": False})
            response = client.get("/api/auth/google", follow_redirects=False)
            self.assertEqual(response.headers["location"], "/?google=unavailable")
