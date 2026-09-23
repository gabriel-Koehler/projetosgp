"""Formatos de entrada e saída (JSON) das rotas de avaliação."""

from pydantic import BaseModel, Field

from app.services.version_builder import Nomenclatura


class QuestaoIn(BaseModel):
    id: str = Field(min_length=1)
    enunciado: str = Field(min_length=1)
    alternativas: list[str] = Field(min_length=2, max_length=26)
    correta: str = Field(min_length=1, max_length=1)


class ConfiguracaoIn(BaseModel):
    quantidade: int = Field(ge=1, le=500)
    nomenclatura: Nomenclatura = Nomenclatura.LETRAS
    nomes_personalizados: list[str] = []
    mesmas_questoes: bool = True
    questoes_por_versao: int | None = Field(default=None, ge=1)
    embaralhar_questoes: bool = False
    embaralhar_alternativas: bool = False


class AvaliacaoIn(BaseModel):
    nome: str = Field(min_length=1)
    semestre: str | None = None
    turma: str | None = None
    questoes: list[QuestaoIn] = Field(min_length=1)
    configuracao: ConfiguracaoIn


class LiberarGabaritoIn(BaseModel):
    liberado: bool


class QuestaoVersaoOut(BaseModel):
    numero: int
    questao_id: str
    enunciado: str
    alternativas: list[str]
    correta: str
    ordem_original: list[str]


class VersaoOut(BaseModel):
    nome: str
    codigo: str
    url_aluno: str
    url_qrcode: str
    questoes: list[QuestaoVersaoOut]
    gabarito: dict[int, str]


class AvaliacaoOut(BaseModel):
    id: int
    nome: str
    semestre: str | None
    turma: str | None
    gabarito_liberado: bool
    versoes: list[VersaoOut]


class ItemGabarito(BaseModel):
    questao: int
    alternativa: str


class GabaritoAlunoOut(BaseModel):
    avaliacao: str
    versao: str
    gabarito: list[ItemGabarito]
