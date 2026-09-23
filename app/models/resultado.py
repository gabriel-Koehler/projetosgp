"""Resultado da correção de uma folha (RF39)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Resultado:
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
    respostas: dict[int, str | None]
    gabarito: dict[int, str]
    acertos: int
    erros: int
    em_branco: int
    anuladas: int
    nota: float
    nota_maxima: float
    origem: str
    imagem_path: str | None
    corrigido_em: datetime


@dataclass
class QuestaoDaVersao:
    """Liga a questão de uma versão à questão original do banco (para as estatísticas)."""

    versao_id: int
    numero: int
    questao_id: int | None
    enunciado: str
    ordem_original: list[str]
