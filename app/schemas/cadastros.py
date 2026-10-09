"""Formatos JSON de semestres, turmas, alunos, questões e importações."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SemestreIn(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    data_inicio: date | None = None
    data_fim: date | None = None


class SemestreOut(BaseModel):
    id: int
    nome: str
    data_inicio: date | None
    data_fim: date | None
    ativo: bool


class AtivoIn(BaseModel):
    ativo: bool


class TurmaIn(BaseModel):
    semestre_id: int
    nome: str = Field(min_length=1, max_length=100)
    disciplina: str | None = Field(default=None, max_length=200)


class TurmaOut(BaseModel):
    id: int
    semestre_id: int
    semestre_nome: str
    nome: str
    disciplina: str | None


class AlunoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    matricula: str = Field(min_length=1, max_length=50)
    email: str | None = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AlunoOut(BaseModel):
    id: int
    turma_id: int
    nome: str
    matricula: str
    email: str | None


class QuestaoIn(BaseModel):
    enunciado: str = Field(min_length=1, max_length=5000)
    alternativas: list[str] = Field(
        min_length=4, max_length=5, description="Textos das alternativas A, B, C, D (E opcional)"
    )
    correta: str = Field(min_length=1, max_length=1, description="Letra da alternativa correta")
    disciplina: str | None = Field(default=None, max_length=200)
    categoria: str | None = Field(default=None, max_length=200)
    dificuldade: Literal["facil", "media", "dificil"] | None = None


class QuestaoOut(BaseModel):
    id: int
    enunciado: str
    alternativas: list[str]
    correta: str
    disciplina: str | None
    categoria: str | None
    dificuldade: str | None
    criado_em: datetime | None
    atualizado_em: datetime | None


class PaginaQuestoes(BaseModel):
    itens: list[QuestaoOut]
    total: int
    pagina: int
    por_pagina: int


class FiltrosQuestoes(BaseModel):
    disciplina: list[str]
    categoria: list[str]


class ExclusaoQuestaoOut(BaseModel):
    excluida: bool
    arquivada: bool
    mensagem: str


class ErroLinhaOut(BaseModel):
    linha: int
    mensagens: list[str]


class LinhaValidaOut(BaseModel):
    linha: int
    dados: dict


class ImportacaoOut(BaseModel):
    confirmado: bool
    total_linhas: int
    validas: list[LinhaValidaOut]
    erros: list[ErroLinhaOut]
    importados: int
