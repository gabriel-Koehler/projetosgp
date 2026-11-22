"""Formatos de entrada e saída (JSON) das rotas de autenticação."""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class LoginRequest(BaseModel):
    username: str
    password: str


Username = Annotated[str, StringConstraints(
    strip_whitespace=True, pattern=r"^[A-Za-z0-9._-]{3,40}$"
)]


class RegisterRequest(BaseModel):
    username: Username
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    email: Annotated[str, StringConstraints(
        strip_whitespace=True, max_length=200, pattern=r"^[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)+$"
    )]
    password: str = Field(min_length=8, max_length=128)
    passwordConfirmation: str = Field(max_length=128)


class ProfessorResponse(BaseModel):
    username: str
    nome: str
