import unittest
from time import time
from fastapi.testclient import TestClient
from app.main import app, provider
from app.mocks.data_provider import initial_state


class MockApiTest(unittest.TestCase):
    def setUp(self):
        with provider.lock:
            provider.states["professor"] = initial_state()
        self.client = TestClient(app)
        response = self.client.post("/api/auth/login", json={"email": "professor", "password": "123456"})
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client.close()

    def create_evaluation(self):
        response = self.client.post("/api/avaliacoes", json={
            "name": "N1", "classId": "c1", "questionIds": ["Q-047", "Q-046"],
            "versionCount": 3, "shuffleQuestions": True, "shuffleAlternatives": True,
        })
        self.assertEqual(response.status_code, 201)
        return response.json()["data"]

    def test_required_routes_filters_and_relations(self):
        for path in ["semestres", "turmas", "alunos", "questoes"]:
            self.assertEqual(self.client.get("/api/" + path).status_code, 200)
        self.assertEqual(self.client.get("/api/turmas?semestre_id=s2").json()["data"], [])
        self.assertEqual(len(self.client.get("/api/alunos?turma_id=c1").json()["data"]), 8)
        self.assertEqual(len(self.client.get("/api/questoes?q=contrato").json()["data"]), 1)
        semester = self.client.post("/api/semestres", json={"name": "2027.1"}).json()["data"]
        classroom = self.client.post("/api/turmas", json={"name": "Nova turma", "code": "NOVA", "semesterId": semester["id"]}).json()["data"]
        self.assertEqual(self.client.post("/api/alunos", json={"name": "Aluno", "registration": "123", "classId": classroom["id"]}).status_code, 201)
        self.assertEqual(self.client.post("/api/alunos", json={"name": "Aluno", "registration": "123", "classId": classroom["id"]}).status_code, 409)
        self.assertEqual(self.client.post("/api/turmas", json={"name": "Inválida", "code": "INV", "semesterId": "missing"}).status_code, 400)

    def test_session_expiration_and_logout(self):
        anonymous = TestClient(app)
        self.assertEqual(anonymous.get("/api/questoes").status_code, 401)
        anonymous.close()
        token = self.client.cookies.get("avalia_session")
        provider.sessions[token]["expires"] = time() - 1
        self.assertEqual(self.client.get("/api/auth/me").status_code, 401)
        self.client.post("/api/auth/login", json={"email": "professor", "password": "123456"})
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)
        self.assertEqual(self.client.get("/api/questoes").status_code, 401)

    def test_invalid_login_and_payload(self):
        self.assertEqual(self.client.post("/api/auth/login", json={"email": "professor", "password": "bad"}).status_code, 401)
        for payload in [{}, {"statement": "x", "options": ["a"]}]:
            response = self.client.post("/api/questoes", json=payload)
            self.assertEqual(response.status_code, 400)
            self.assertIn("message", response.json()["error"])
        self.assertEqual(self.client.post("/api/semestres", content="{", headers={"Content-Type": "application/json"}).status_code, 400)
        self.assertEqual(self.client.post("/api/avaliacoes", json={"name": "X", "classId": "c1", "questionIds": ["Q-047"], "versionCount": 500}).status_code, 400)

    def test_question_crud_preserves_existing_versions(self):
        evaluation = self.create_evaluation()
        self.assertEqual(self.client.delete("/api/questoes/Q-047").status_code, 200)
        self.assertEqual(self.client.delete("/api/questoes/Q-047").status_code, 404)
        stored = self.client.get("/api/avaliacoes").json()["data"][0]
        self.assertEqual(stored, evaluation)
        self.assertEqual(self.client.post("/api/questoes", json={
            "statement": "Qual alternativa?", "subject": "Teste", "difficulty": "Fácil",
            "options": ["Um", "Dois", "Três", "Quatro"], "answer": "C",
        }).status_code, 201)

    def test_versions_qr_and_grading(self):
        evaluation = self.create_evaluation()
        self.assertEqual(len(evaluation["versions"]), 3)
        for version in evaluation["versions"]:
            self.assertEqual({q["id"] for q in version["questions"]}, {"Q-047", "Q-046"})
            for question in version["questions"]:
                self.assertEqual(question["options"][ord(question["answerLetter"]) - 65], question["correctAnswer"])
        qr = self.client.get("/api/avaliacoes/" + evaluation["id"] + "/qr/A")
        self.assertTrue(qr.json()["data"]["image"].startswith("data:image/png;base64,"))
        answers = [q["answerLetter"] for q in evaluation["versions"][0]["questions"]]
        payload = {"evaluationId": evaluation["id"], "studentId": "a1", "version": "A", "answers": answers}
        response = self.client.post("/api/resultados", json=payload)
        self.assertEqual(response.json()["data"]["grade"], 10)
        self.assertEqual(self.client.post("/api/resultados", json=payload).status_code, 409)
        wrong = ["B" if answer == "A" else "A" for answer in answers]
        self.assertEqual(self.client.post("/api/resultados", json={**payload, "studentId": "a2", "answers": wrong}).json()["data"]["grade"], 0)
        self.assertEqual(self.client.post("/api/resultados", json={**payload, "studentId": "missing"}).status_code, 400)

    def test_accounts_are_isolated(self):
        self.create_evaluation()
        other = TestClient(app)
        from uuid import uuid4
        registration = {"name": "Outra conta", "email": str(uuid4()) + "@example.com", "password": "123456"}
        self.assertEqual(other.post("/api/auth/register", json=registration).status_code, 200)
        self.assertEqual(other.get("/api/avaliacoes").json()["data"], [])
        self.assertEqual(other.post("/api/auth/register", json=registration).status_code, 409)
        self.assertEqual(len(self.client.get("/api/avaliacoes").json()["data"]), 1)
        other.close()

    def test_recovery_is_explicitly_simulated(self):
        response = self.client.post("/api/auth/recovery", json={"email": "professor@example.com"})
        self.assertIn("simulada", response.json()["data"]["message"])
        self.assertEqual(self.client.post("/api/auth/recovery", json={"email": "invalid"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()

