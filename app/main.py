"""API local de demonstração N1-BE-02, compatível com o cliente AvaliaSystem."""
import base64
import io
import json
import random
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Annotated, Literal
from uuid import uuid4

import qrcode
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.mocks.data_provider import MemoryProvider

provider = MemoryProvider()
app = FastAPI(title="AvaliaSystem Mock API", version="1.0.0")
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Identifier = Annotated[str, StringConstraints(min_length=1, max_length=100)]
Password = Annotated[str, StringConstraints(min_length=6, max_length=128)]
Letter = Literal["A", "B", "C", "D"]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Login(Payload):
    email: Text
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class Recovery(Payload):
    email: Text

    @field_validator("email")
    @classmethod
    def email_format(cls, value):
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Informe um e-mail válido.")
        return value.lower()


class Register(Recovery):
    name: Text
    password: Password


class Semester(Payload):
    name: Text


class ClassRoom(Payload):
    name: Text
    code: Text
    semesterId: Identifier


class Student(Payload):
    name: Text
    registration: Text
    classId: Identifier


class Question(Payload):
    statement: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    subject: Text
    difficulty: Literal["Fácil", "Médio", "Difícil"]
    options: list[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]] = Field(min_length=4, max_length=4)
    answer: Letter


class Evaluation(Payload):
    name: Text
    classId: Identifier
    questionIds: list[Identifier] = Field(min_length=1, max_length=100)
    versionCount: int = Field(ge=1, le=5, strict=True)
    shuffleQuestions: bool = False
    shuffleAlternatives: bool = False


class Result(Payload):
    evaluationId: Identifier
    studentId: Identifier
    version: Annotated[str, StringConstraints(pattern="^[A-E]$")]
    answers: list[Letter] = Field(min_length=1, max_length=100)


def data(value):
    return {"data": value}


def missing(message="Recurso não encontrado."):
    raise HTTPException(404, message)


@app.exception_handler(HTTPException)
async def http_error(request, error):
    return JSONResponse(status_code=error.status_code, content={"error": {"message": str(error.detail)}})


@app.exception_handler(RequestValidationError)
async def invalid_payload(request, error):
    fields = ", ".join(dict.fromkeys(str(e["loc"][-1]) for e in error.errors()))
    return JSONResponse(status_code=400, content={"error": {"message": "Verifique os campos obrigatórios e seus valores: " + fields}})


def current_user(request: Request):
    user = provider.session_user(request.cookies.get("avalia_session"))
    if not user:
        raise HTTPException(401, "Sua sessão expirou. Entre novamente.")
    return user


def current_state(user=Depends(current_user)):
    return provider.states[user["id"]]


def sign_in(user, request, response):
    token = provider.create_session(user["id"], request.cookies.get("avalia_session"))
    response.set_cookie("avalia_session", token, httponly=True, samesite="lax", max_age=3600, path="/")
    return data(provider.public_user(user))


@app.get("/health")
def health():
    return {"status": "ok", "storage": "memory", "mode": "mock"}


@app.post("/api/auth/login")
def login(body: Login, request: Request, response: Response):
    user = provider.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(401, "E-mail ou senha inválidos.")
    return sign_in(user, request, response)


@app.post("/api/auth/register")
def register(body: Register, request: Request, response: Response):
    try:
        user = provider.add_user(body.name, body.email, body.password)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    return sign_in(user, request, response)


@app.post("/api/auth/recovery")
def recovery(body: Recovery):
    return data({"message": "Solicitação simulada. Este MVP não envia e-mails; use a conta de demonstração ou crie uma conta."})


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    with provider.lock:
        provider.sessions.pop(request.cookies.get("avalia_session"), None)
    response.delete_cookie("avalia_session", path="/")
    return data(None)


@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return data(provider.public_user(user))


@app.get("/api/workspace")
def workspace(state=Depends(current_state)):
    with provider.lock:
        return data(deepcopy(state))


@app.get("/api/semestres")
@app.get("/api/semesters", include_in_schema=False)
def semesters(state=Depends(current_state)):
    return data(deepcopy(state["semesters"]))


@app.post("/api/semestres", status_code=201)
@app.post("/api/semesters", status_code=201, include_in_schema=False)
def add_semester(body: Semester, state=Depends(current_state)):
    with provider.lock:
        if any(s["name"] == body.name for s in state["semesters"]):
            raise HTTPException(409, "Semestre já cadastrado.")
        item = {"id": str(uuid4()), **body.model_dump(), "active": False}
        state["semesters"].append(item)
        return data(item)


@app.get("/api/turmas")
@app.get("/api/classes", include_in_schema=False)
def classes(semestre_id: str | None = None, state=Depends(current_state)):
    return data([deepcopy(c) for c in state["classes"] if not semestre_id or c["semesterId"] == semestre_id])


@app.post("/api/turmas", status_code=201)
@app.post("/api/classes", status_code=201, include_in_schema=False)
def add_class(body: ClassRoom, state=Depends(current_state)):
    with provider.lock:
        if not any(s["id"] == body.semesterId for s in state["semesters"]):
            raise HTTPException(400, "Semestre não encontrado.")
        if any(c["code"] == body.code for c in state["classes"]):
            raise HTTPException(409, "Código de turma já cadastrado.")
        item = {"id": str(uuid4()), **body.model_dump()}
        state["classes"].append(item)
        return data(item)


@app.get("/api/alunos")
@app.get("/api/students", include_in_schema=False)
def students(turma_id: str | None = None, state=Depends(current_state)):
    return data([deepcopy(a) for a in state["students"] if not turma_id or a["classId"] == turma_id])


@app.post("/api/alunos", status_code=201)
@app.post("/api/students", status_code=201, include_in_schema=False)
def add_student(body: Student, state=Depends(current_state)):
    with provider.lock:
        if not any(c["id"] == body.classId for c in state["classes"]):
            raise HTTPException(400, "Turma não encontrada.")
        if any(a["registration"] == body.registration for a in state["students"]):
            raise HTTPException(409, "Matrícula já cadastrada.")
        item = {"id": str(uuid4()), **body.model_dump()}
        state["students"].append(item)
        return data(item)


@app.get("/api/questoes")
@app.get("/api/questions", include_in_schema=False)
def questions(q: str = "", state=Depends(current_state)):
    return data([deepcopy(item) for item in state["questions"] if q.casefold() in (item["statement"] + " " + item["subject"]).casefold()])


@app.post("/api/questoes", status_code=201)
@app.post("/api/questions", status_code=201, include_in_schema=False)
def add_question(body: Question, state=Depends(current_state)):
    with provider.lock:
        item = {"id": str(uuid4()), **body.model_dump()}
        state["questions"].append(item)
        return data(item)


@app.delete("/api/questoes/{question_id}")
@app.delete("/api/questions/{question_id}", include_in_schema=False)
def delete_question(question_id: str, state=Depends(current_state)):
    with provider.lock:
        question = next((q for q in state["questions"] if q["id"] == question_id), None)
        if not question:
            missing("Questão não encontrada.")
        state["questions"].remove(question)
        return data(None)


@app.get("/api/avaliacoes")
@app.get("/api/evaluations", include_in_schema=False)
def evaluations(state=Depends(current_state)):
    return data(deepcopy(state["evaluations"]))


@app.post("/api/avaliacoes", status_code=201)
@app.post("/api/evaluations", status_code=201, include_in_schema=False)
def add_evaluation(body: Evaluation, state=Depends(current_state)):
    with provider.lock:
        if not any(c["id"] == body.classId for c in state["classes"]):
            raise HTTPException(400, "Turma não encontrada.")
        bank = {q["id"]: q for q in state["questions"]}
        if len(set(body.questionIds)) != len(body.questionIds) or any(i not in bank for i in body.questionIds):
            raise HTTPException(400, "Selecione questões existentes e sem repetições.")
        versions = []
        for index in range(body.versionCount):
            selected = [deepcopy(bank[i]) for i in body.questionIds]
            if body.shuffleQuestions:
                random.shuffle(selected)
            for question in selected:
                # Keep original index identity, including when two alternatives have equal text.
                correct_index = ord(question["answer"]) - 65
                indexed = list(enumerate(question["options"]))
                if body.shuffleAlternatives:
                    random.shuffle(indexed)
                letter = chr(65 + next(i for i, (original, _) in enumerate(indexed) if original == correct_index))
                correct = question["options"][correct_index]
                question.update(options=[text for _, text in indexed], answer=correct, correctAnswer=correct,
                                answerLetter=letter, originalQuestionId=question["id"], versionName=chr(65 + index))
            versions.append({"name": chr(65 + index), "questions": selected, "answerKey": [
                {"questionId": q["id"], "position": i, "correct": q["correctAnswer"]}
                for i, q in enumerate(selected)
            ]})
        item = {"id": str(uuid4()), "name": body.name, "classId": body.classId,
                "createdAt": datetime.now(timezone.utc).isoformat(), "versions": versions}
        state["evaluations"].append(item)
        return data(item)


@app.get("/api/avaliacoes/{evaluation_id}/qr/{version}")
@app.get("/api/evaluations/{evaluation_id}/qr/{version}", include_in_schema=False)
def qr(evaluation_id: str, version: str, state=Depends(current_state)):
    evaluation = next((e for e in state["evaluations"] if e["id"] == evaluation_id), None)
    if not evaluation or not any(v["name"] == version for v in evaluation["versions"]):
        missing("Versão não encontrada.")
    payload = json.dumps({"evaluationId": evaluation_id, "version": version})
    buffer = io.BytesIO()
    qrcode.make(payload).save(buffer, format="PNG")
    return data({"image": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode(), "payload": payload})


@app.get("/api/resultados")
@app.get("/api/results", include_in_schema=False)
def results(state=Depends(current_state)):
    return data(deepcopy(state["results"]))


@app.post("/api/resultados", status_code=201)
@app.post("/api/results", status_code=201, include_in_schema=False)
def add_result(body: Result, state=Depends(current_state)):
    with provider.lock:
        evaluation = next((e for e in state["evaluations"] if e["id"] == body.evaluationId), None)
        if not evaluation:
            raise HTTPException(400, "Avaliação não encontrada.")
        version = next((v for v in evaluation["versions"] if v["name"] == body.version), None)
        if not version or len(body.answers) != len(version["questions"]):
            raise HTTPException(400, "Versão ou quantidade de respostas inválida.")
        if not any(a["id"] == body.studentId and a["classId"] == evaluation["classId"] for a in state["students"]):
            raise HTTPException(400, "Aluno não pertence à turma da avaliação.")
        if any(r["evaluationId"] == body.evaluationId and r["studentId"] == body.studentId for r in state["results"]):
            raise HTTPException(409, "Este aluno já possui resultado nesta avaliação.")
        correct = sum(q["answerLetter"] == answer for q, answer in zip(version["questions"], body.answers))
        item = {"id": str(uuid4()), **body.model_dump(), "correct": correct, "total": len(body.answers),
                "grade": round(10 * correct / len(body.answers), 1), "createdAt": datetime.now(timezone.utc).isoformat()}
        state["results"].append(item)
        return data(item)

