"""Formatos de entrada e saída (JSON) das rotas de avaliação."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.services.version_builder import Nomenclatura


class ConfiguracaoIn(BaseModel):
    quantidade: int = Field(ge=1, le=500)
    nomenclatura: Nomenclatura = Nomenclatura.LETRAS
    nomes_personalizados: list[str] = []
    mesmas_questoes: bool = True
    questoes_por_versao: int | None = Field(default=None, ge=1)
    embaralhar_questoes: bool = False
    embaralhar_alternativas: bool = False


class AvaliacaoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    turma_id: int | None = None
    questao_ids: list[int] = Field(min_length=1, description="Questões do banco, na ordem da prova")
    # RF16: ajuste do gabarito só nesta avaliação, ex.: {"12": "C"}.
    gabaritos: dict[int, str] = {}
    nota_maxima: float = Field(default=10, gt=0, le=1000)
    configuracao: ConfiguracaoIn


class LiberarGabaritoIn(BaseModel):
    liberado: bool


class QuestaoVersaoOut(BaseModel):
    numero: int
    questao_id: str | None
    enunciado: str
    alternativas: list[str]
    correta: str
    ordem_original: list[str]


class VersaoOut(BaseModel):
    id: int
    nome: str
    codigo: str
    url_aluno: str
    url_qrcode: str
    questoes: list[QuestaoVersaoOut]
    gabarito: dict[int, str]


class ResumoAvaliacaoOut(BaseModel):
    id: int
    nome: str
    turma_id: int | None
    turma_nome: str | None
    semestre_nome: str | None
    nota_maxima: float
    gabarito_liberado: bool
    criada_em: datetime
    quantidade_versoes: int
    quantidade_questoes: int


class AvaliacaoOut(BaseModel):
    id: int
    nome: str
    turma_id: int | None
    turma_nome: str | None
    semestre_nome: str | None
    nota_maxima: float
    configuracao: dict
    gabarito_liberado: bool
    criada_em: datetime
    versoes: list[VersaoOut]


class ItemGabarito(BaseModel):
    questao: int
    alternativa: str


class GabaritoAlunoOut(BaseModel):
    avaliacao: str
    versao: str
    gabarito: list[ItemGabarito]
