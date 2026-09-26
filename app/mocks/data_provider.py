"""Dados fictícios em memória. Reiniciar o processo restaura o estado inicial."""
from copy import deepcopy
from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_urlsafe, token_bytes
from threading import RLock
from time import time
from uuid import uuid4

SEMESTRES = [
    {"id": "s1", "name": "2026.1", "active": True},
    {"id": "s2", "name": "2025.2", "active": False},
    {"id": "s3", "name": "2025.1", "active": False},
]
TURMAS = [
    {"id": "c1", "semesterId": "s1", "name": "Direito Civil I", "code": "DC-2026A"},
    {"id": "c2", "semesterId": "s1", "name": "Direito Constitucional", "code": "DCON-2026A"},
    {"id": "c3", "semesterId": "s1", "name": "Direito Penal I", "code": "DP-2026A"},
    {"id": "c4", "semesterId": "s1", "name": "Direito Processual Civil", "code": "DPC-2026A"},
    {"id": "c5", "semesterId": "s1", "name": "Direito do Trabalho", "code": "DT-2026A"},
]
ALUNOS = [
    {"id": "a" + str(i + 1), "classId": "c1", "name": name, "registration": str(2024001 + i)}
    for i, name in enumerate([
        "Ana Clara Ferreira", "Bruno Alves Costa", "Camila Oliveira", "Diego Santos",
        "Elena Rodrigues", "Felipe Lima", "Gabriela Souza", "Henrique Martins",
    ])
]
QUESTOES = [
    {
        "id": "Q-047", "subject": "Direito Civil", "difficulty": "Médio",
        "statement": "Qual dos seguintes elementos é essencial para a validade de um contrato conforme o Código Civil Brasileiro?",
        "options": ["Forma escrita", "Agente capaz, objeto lícito e forma prescrita ou não defesa em lei", "Testemunhas", "Registro em cartório"],
        "answer": "B",
    },
    {
        "id": "Q-046", "subject": "Direito Civil", "difficulty": "Fácil",
        "statement": "O que caracteriza a obrigação de dar coisa certa no Direito Civil?",
        "options": ["Entrega de coisa individuada e determinada", "Entrega de qualquer bem fungível", "Prestação de serviço específico", "Pagamento em dinheiro"],
        "answer": "A",
    },
]


def initial_state():
    return {
        "semesters": deepcopy(SEMESTRES), "classes": deepcopy(TURMAS),
        "students": deepcopy(ALUNOS), "questions": deepcopy(QUESTOES),
        "evaluations": [], "results": [],
    }


class MemoryProvider:
    """Estado por professor; as sementes nunca são alteradas pelas requisições."""
    def __init__(self):
        self.lock = RLock()
        self.users = {}
        self.states = {}
        self.sessions = {}
        self.add_user("Prof. Dr. Carlos Silva", "professor@avaliasystem.com", "123456", "professor")

    def add_user(self, name, email, password, user_id=None):
        with self.lock:
            if any(u["email"] == email.lower() for u in self.users.values()):
                raise ValueError("Já existe uma conta com esse e-mail.")
            salt = token_bytes(16)
            user = {
                "id": user_id or str(uuid4()), "name": name, "email": email.lower(),
                "salt": salt, "password": pbkdf2_hmac("sha256", password.encode(), salt, 120000),
            }
            self.users[user["id"]] = user
            self.states[user["id"]] = initial_state()
            return user

    def authenticate(self, email, password):
        email = "professor@avaliasystem.com" if email == "professor" else email.lower()
        with self.lock:
            user = next((u for u in self.users.values() if u["email"] == email), None)
            if user and compare_digest(user["password"], pbkdf2_hmac("sha256", password.encode(), user["salt"], 120000)):
                return user
        return None

    def create_session(self, user_id, previous=None):
        with self.lock:
            now = time()
            self.sessions = {k: v for k, v in self.sessions.items() if v["expires"] > now}
            self.sessions.pop(previous, None)
            token = token_urlsafe(32)
            self.sessions[token] = {"userId": user_id, "expires": now + 3600}
            return token

    def session_user(self, token):
        with self.lock:
            session = self.sessions.get(token)
            if not session or session["expires"] <= time():
                self.sessions.pop(token, None)
                return None
            return self.users.get(session["userId"])

    @staticmethod
    def public_user(user):
        return {key: user[key] for key in ("id", "name", "email")}

