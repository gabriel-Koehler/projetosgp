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

    def test_statistics_track_original_alternatives_across_versions(self):
        # Equal text must not collapse two distinct alternative identities.
        q = self.client.post("/api/questoes", json={"statement": "Duplicadas", "subject": "QA", "difficulty": "Fácil",
            "options": ["Igual", "Igual", "Três", "Quatro"], "answer": "B"}).json()["data"]
        evaluation = self.client.post("/api/avaliacoes", json={"name": "Estatísticas", "classId": "c1",
            "questionIds": [q["id"], "Q-047"], "versionCount": 3, "shuffleQuestions": True,
            "shuffleAlternatives": True}).json()["data"]
        path = "/api/avaliacoes/" + evaluation["id"] + "/estatisticas"
        empty = self.client.get(path).json()["data"]
        self.assertEqual(empty["count"], 0)
        self.assertIsNone(empty["average"])
        self.assertTrue(all(x["hitRate"] is None and x["mostSelected"] == [] for x in empty["questions"]))
        for index, version in enumerate(evaluation["versions"]):
            original = [1, 0, 2][index]
            answers = [chr(65 + item["optionOriginalIndices"].index(original)) if item["id"] == q["id"]
                       else item["answerLetter"] for item in version["questions"]]
            response = self.client.post("/api/resultados", json={"evaluationId": evaluation["id"],
                "studentId": "a" + str(index + 1), "version": version["name"], "answers": answers})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()["data"]["grade"], 10 if index == 0 else 5)
        # Statistics depend on evaluation snapshots, not the current question bank.
        self.client.delete("/api/questoes/" + q["id"])
        stats = self.client.get(path).json()["data"]
        self.assertEqual((stats["count"], stats["average"]), (3, 6.7))
        question = next(x for x in stats["questions"] if x["id"] == q["id"])
        self.assertEqual((question["correct"], question["total"], question["hitRate"]), (1, 3, 33.3))
        self.assertEqual([a["count"] for a in question["alternatives"]], [1, 1, 1, 0])
        self.assertEqual(question["mostSelected"], [0, 1, 2])
        self.assertEqual(self.client.get(path + "?student_id=a1").json()["data"]["average"], 10)
        self.assertEqual(self.client.get(path + "?student_id=unknown").json()["data"]["count"], 0)
        with TestClient(app) as other:
            self.assertEqual(other.get(path).status_code, 401)
            other.post("/api/auth/register", json={"name": "Isolado", "email": "stats-" + str(time()) + "@test.com", "password": "123456"})
            self.assertEqual(other.get(path).status_code, 404)

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

    def test_batch_import_validates_atomically(self):
        original = len(self.client.get("/api/alunos").json()["data"])
        payload = {"classId": "c2", "students": [{"name": "Novo", "registration": "001"}, {"name": "Duplicado", "registration": "2024001"}]}
        self.assertEqual(self.client.post("/api/alunos/import", json=payload).status_code, 409)
        self.assertEqual(len(self.client.get("/api/alunos").json()["data"]), original)
        payload["students"][1]["registration"] = "002"
        result = self.client.post("/api/alunos/import", json=payload)
        self.assertEqual(result.status_code, 201)
        self.assertTrue(all(a["classId"] == "c2" for a in result.json()["data"]))
        self.assertEqual(result.json()["data"][0]["registration"], "001")
        self.assertEqual(self.client.post("/api/alunos/import", json=payload).status_code, 409)
        self.assertEqual(self.client.post("/api/alunos/import", json={"classId": "missing", "students": [{"name": "A", "registration": "003"}]}).status_code, 400)

    def test_question_edit_and_import_preserve_snapshots(self):
        evaluation = self.create_evaluation()
        question = {"statement": "Editada", "subject": "Teste", "difficulty": "Médio", "options": ["Um", "Dois", "Três", "Quatro"], "answer": "D"}
        self.assertEqual(self.client.put("/api/questoes/Q-047", json=question).status_code, 200)
        self.assertEqual(self.client.get("/api/avaliacoes").json()["data"][0], evaluation)
        self.assertEqual(self.client.put("/api/questoes/missing", json=question).status_code, 404)
        payload = {"questions": [{**question, "statement": "Nova"}, question]}
        before = len(self.client.get("/api/questoes").json()["data"])
        self.assertEqual(self.client.post("/api/questoes/import", json=payload).status_code, 409)
        self.assertEqual(len(self.client.get("/api/questoes").json()["data"]), before)
        payload["questions"].pop()
        self.assertEqual(self.client.post("/api/questoes/import", json=payload).status_code, 201)
        self.assertEqual(self.client.post("/api/questoes/import", json={"questions": [{**question, "answer": "Z"}]}).status_code, 400)

    def test_named_versions_validation_order_and_correction(self):
        body = {"name": "Prova", "classId": "c1", "questionIds": ["Q-047", "Q-046"],
                "versionCount": 2, "versionNames": ["Azul", "Versão Verde"],
                "shuffleQuestions": False, "shuffleAlternatives": False}
        for names in [["A"], ["Azul", "azul"], ["", "B"], ["A/B", "C"]]:
            self.assertEqual(self.client.post("/api/avaliacoes", json={**body, "versionNames": names}).status_code, 400)
        result = self.client.post("/api/avaliacoes", json=body)
        self.assertEqual(result.status_code, 201)
        evaluation = result.json()["data"]
        self.assertEqual([v["name"] for v in evaluation["versions"]], ["Azul", "Versão Verde"])
        for version in evaluation["versions"]:
            self.assertEqual([q["id"] for q in version["questions"]], body["questionIds"])
            self.assertEqual([q["answerLetter"] for q in version["questions"]], ["B", "A"])
            self.assertTrue(all(q["versionName"] == version["name"] for q in version["questions"]))
        from urllib.parse import quote
        self.assertEqual(self.client.get("/api/avaliacoes/" + evaluation["id"] + "/qr/" + quote("Versão Verde")).status_code, 200)
        corrected = self.client.post("/api/resultados", json={"evaluationId": evaluation["id"], "studentId": "a1", "version": "Versão Verde", "answers": ["B", "A"]})
        self.assertEqual(corrected.json()["data"]["grade"], 10)

    def test_public_answer_key_is_explicit_restricted_and_revocable(self):
        evaluation = self.create_evaluation()
        endpoint = "/api/avaliacoes/" + evaluation["id"] + "/versoes/A/publicar"
        anonymous = TestClient(app)
        self.assertEqual(anonymous.post(endpoint).status_code, 401)
        self.assertEqual(anonymous.get("/api/avaliacoes/" + evaluation["id"]).status_code, 401)
        self.assertEqual(anonymous.get("/api/public/gabaritos/missing").status_code, 404)
        published = self.client.post(endpoint).json()["data"]["path"]
        token = published.split("token=")[1]
        content = anonymous.get("/api/public/gabaritos/" + token).json()["data"]
        self.assertEqual(set(content), {"name", "version", "questions"})
        self.assertEqual(set(content["questions"][0]), {"position", "statement", "answerLetter", "correctAnswer"})
        self.assertEqual(content["questions"][0]["answerLetter"], evaluation["versions"][0]["questions"][0]["answerLetter"])
        self.assertEqual(self.client.post(endpoint).json()["data"]["path"], published)
        self.assertEqual(self.client.delete(endpoint).status_code, 200)
        self.assertEqual(anonymous.get("/api/public/gabaritos/" + token).status_code, 404)
        anonymous.close()

    def test_recovery_is_explicitly_simulated(self):
        response = self.client.post("/api/auth/recovery", json={"email": "professor@example.com"})
        self.assertIn("simulada", response.json()["data"]["message"])
        self.assertEqual(self.client.post("/api/auth/recovery", json={"email": "invalid"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()

