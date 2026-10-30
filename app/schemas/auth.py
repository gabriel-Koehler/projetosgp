"""Formatos de entrada e saída (JSON) das rotas de autenticação."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfessorResponse(BaseModel):
    username: str
    nome: str
