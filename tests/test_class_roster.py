import io
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.main import app


class ClassRosterTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        password = "senha-professor-123"
        signup = self.client.post("/api/auth/register", json={
            "name": "Professor Teste", "username": "prof." + uuid4().hex[:12],
            "password": password, "passwordConfirmation": password,
        })
        self.assertEqual(signup.status_code, 200)
        semestre = self.client.post("/api/semestres", json={"name": "Semestre de teste"})
        self.assertEqual(semestre.status_code, 201)
        self.semestre_id = semestre.json()["data"]["id"]
        self.path = self.create_class()

    def create_class(self):
        turma = self.client.post("/api/turmas", json={
            "name": "Turma de teste", "code": uuid4().hex, "semesterId": self.semestre_id,
        })
        self.assertEqual(turma.status_code, 201)
        return f"/api/turmas/{turma.json()['data']['id']}/alunos"

    def test_manage_students_and_scope_registration_to_class(self):
        student = {"nome": "Ana Silva", "matricula": "000123"}
        self.assertEqual(self.client.post(self.path, json=dict(student, nome=" ")).status_code, 400)
        created = self.client.post(self.path, json=student)
        self.assertEqual(created.status_code, 201)
        aluno = created.json()["data"]
        self.assertIsNone(aluno["email"])
        self.assertEqual(self.client.post(self.path, json=student).status_code, 409)
        self.assertEqual(self.client.post(self.create_class(), json=student).status_code, 201)

        path = f"/api/alunos/{aluno['id']}"
        updated = self.client.put(path, json=dict(student, nome="Ana Lima", email="ana@example.com"))
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(self.client.get(self.path).json()["data"][0]["nome"], "Ana Lima")
        self.assertEqual(self.client.delete(path).status_code, 204)
        self.assertEqual(self.client.get(self.path).json()["data"], [])

    def test_download_filled_template_preview_and_import(self):
        download = self.client.get("/api/alunos/modelo.xlsx")
        self.assertEqual(download.status_code, 200)
        self.assertIn('filename="modelo_alunos.xlsx"', download.headers["content-disposition"])
        workbook = load_workbook(io.BytesIO(download.content))
        sheet = workbook["Alunos"]
        self.assertEqual(workbook.active.title, "Alunos")
        self.assertIn("Instruções", workbook.sheetnames)
        self.assertEqual([cell.value for cell in sheet[1]], ["nome", "matricula", "email"])
        self.assertEqual(sheet["B2"].number_format, "@")
        self.assertEqual(sheet.column_dimensions["B"].number_format, "@")
        self.assertEqual(sheet.freeze_panes, "A2")
        sheet["A2"] = "Ana Silva"
        sheet["B2"] = "000042"
        sheet["C2"] = None
        sheet.append(["Duplicada", "000042", None])
        sheet.append(["Sem matrícula", None, None])
        sheet.append(["Nome longo " * 21, "344", None])
        workbook.active = workbook["Instruções"]
        output = io.BytesIO()
        workbook.save(output)
        files = {"arquivo": ("alunos.xlsx", output.getvalue())}

        preview = self.client.post(self.path + "/importar", files=files)
        self.assertEqual(preview.status_code, 200)
        data = preview.json()["data"]
        self.assertEqual(data["importados"], 0)
        self.assertEqual([row["linha"] for row in data["erros"]], [3, 4, 5])
        self.assertEqual(data["validas"][0]["dados"]["matricula"], "000042")
        self.assertEqual(self.client.get(self.path).json()["data"], [])

        confirmed = self.client.post(self.path + "/importar?confirmar=true", files=files)
        self.assertEqual(confirmed.json()["data"]["importados"], 1)
        self.assertEqual(self.client.get(self.path).json()["data"][0]["matricula"], "000042")
        repeated = self.client.post(self.path + "/importar?confirmar=true", files=files)
        self.assertEqual(repeated.json()["data"]["importados"], 0)
