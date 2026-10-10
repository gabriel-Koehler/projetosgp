"""Entidades de avaliação: Avaliacao possui várias VersaoAvaliacao (seção 8 dos requisitos)."""

from dataclasses import dataclass, field
from datetime import datetime

from app.services.version_builder import Versao


@dataclass
class VersaoAvaliacao:
    id: int
    # Código aleatório usado no QR Code: não dá para adivinhar o de outra versão.
    codigo: str
    versao: Versao


@dataclass
class ResumoAvaliacao:
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


@dataclass
class Avaliacao:
    id: int
    nome: str
    turma_id: int | None
    turma_nome: str | None
    semestre_nome: str | None
    nota_maxima: float
    configuracao: dict
    gabarito_liberado: bool
    criada_em: datetime
    versoes: list[VersaoAvaliacao] = field(default_factory=list)


@dataclass
class VersaoPorCodigo:
    """O que o código do QR Code identifica: usado pelo aluno e pela correção."""

    avaliacao_id: int
    professor_id: int
    avaliacao_nome: str
    gabarito_liberado: bool
    nota_maxima: float
    versao_id: int
    versao_nome: str
    gabarito: dict[int, str]
    alternativas_por_questao: dict[int, int]  # número da questão -> quantidade de alternativas
