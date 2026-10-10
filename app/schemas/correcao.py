"""Formatos JSON da leitura e correção das folhas de resposta."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

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


class CorrecaoManualIn(BaseModel):
    codigo: str = Field(min_length=1, description="Código da versão (o que está no QR Code)")
    # Número da questão -> letra marcada, null (em branco) ou "*" (mais de uma marcação).
    respostas: dict[int, str | None]
    aluno_id: int | None = None


class QuestaoResultadoOut(BaseModel):
    numero: int
    marcada: str | None
    correta: str
    situacao: Literal["correta", "errada", "em_branco", "anulada"]


class ResultadoOut(BaseModel):
    id: int
    avaliacao_id: int
    avaliacao_nome: str
    versao_id: int
    versao_nome: str
    aluno_id: int | None
    aluno_nome: str | None
    matricula: str | None
    turma_nome: str | None
    semestre_nome: str | None
    acertos: int
    erros: int
    em_branco: int
    anuladas: int
    nota: float
    nota_maxima: float
    origem: Literal["omr", "manual"]
    corrigido_em: datetime
    questoes: list[QuestaoResultadoOut]


class CorrecaoOut(BaseModel):
    resultado: ResultadoOut
    leitura: LeituraOut


class EstatisticaQuestaoOut(BaseModel):
    ordem: int
    questao_id: int
    enunciado: str
    correta: str
    respondentes: int
    acertos: int
    percentual_acerto: float
    escolhas: dict[str, int]
    percentuais: dict[str, float]
    em_branco: int
    anuladas: int
    mais_escolhida: str | None


class FaixaNotaOut(BaseModel):
    de: float
    ate: float
    quantidade: int


class EstatisticaVersaoOut(BaseModel):
    versao: str
    provas: int
    media: float | None


class EstatisticasOut(BaseModel):
    provas_corrigidas: int
    nota_maxima: float
    media: float | None
    mediana: float | None
    maior_nota: float | None
    menor_nota: float | None
    desvio_padrao: float | None
    media_acertos: float | None
    media_erros: float | None
    percentual_acerto: float | None
    distribuicao: list[FaixaNotaOut]
    por_versao: list[EstatisticaVersaoOut]
    por_questao: list[EstatisticaQuestaoOut]
