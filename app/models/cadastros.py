"""Entidades de cadastro: Professor -> Semestre -> Turma -> Aluno, e o banco de questões."""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Professor:
    id: int
    username: str
    nome: str
    senha_hash: str


@dataclass
class Semestre:
    id: int
    nome: str
    data_inicio: date | None
    data_fim: date | None
    ativo: bool


@dataclass
class Turma:
    id: int
    semestre_id: int
    semestre_nome: str
    nome: str
    disciplina: str | None


@dataclass
class Aluno:
    id: int
    turma_id: int
    nome: str
    matricula: str
    email: str | None


@dataclass
class QuestaoBanco:
    id: int
    enunciado: str
    alternativas: list[str]  # na ordem A, B, C...
    correta: str
    disciplina: str | None = None
    categoria: str | None = None
    dificuldade: str | None = None
    arquivada: bool = False
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
