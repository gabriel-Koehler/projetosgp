"""Entidades de avaliação: Avaliacao possui várias VersaoAvaliacao (seção 8 dos requisitos)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.services.version_builder import Versao


@dataclass
class VersaoAvaliacao:
    # Código aleatório usado no QR Code: não dá para adivinhar o de outra versão.
    codigo: str
    versao: Versao


@dataclass
class Avaliacao:
    id: int
    nome: str
    semestre: str | None
    turma: str | None
    versoes: list[VersaoAvaliacao]
    gabarito_liberado: bool = False
    criada_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
