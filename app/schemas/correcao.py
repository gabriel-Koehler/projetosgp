"""Formatos JSON da leitura e correção das folhas de resposta."""

from pydantic import BaseModel

from app.services.omr_service import Situacao


class QuestaoLidaOut(BaseModel):
    numero: int
    situacao: Situacao
    resposta: str | None
    preenchimento: list[float]


class LeituraOut(BaseModel):
    codigo: str
    avaliacao_id: int
    avaliacao: str
    versao: str
    # False = alguma marcação ficou duvidosa: ler de novo ou conferir antes de registrar (RN15).
    confiavel: bool
    mensagem: str
    respostas: dict[int, str | None]
    em_branco: list[int]
    multiplas: list[int]
    ilegiveis: list[int]
    questoes: list[QuestaoLidaOut]
