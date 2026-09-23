"""Armazenamento em memória das avaliações geradas (mock da N1).

Na N2 é substituído pela persistência no Supabase [N2-BE-04].
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from threading import Lock

from app.core.version_builder import Versao


@dataclass
class VersaoArmazenada:
    # Código aleatório usado no QR Code: não dá para adivinhar o de outra versão.
    codigo: str
    versao: Versao


@dataclass
class Avaliacao:
    id: int
    nome: str
    semestre: str | None
    turma: str | None
    versoes: list[VersaoArmazenada]
    gabarito_liberado: bool = False
    criada_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AvaliacoesStore:
    def __init__(self) -> None:
        self._avaliacoes: dict[int, Avaliacao] = {}
        self._por_codigo: dict[str, tuple[Avaliacao, VersaoArmazenada]] = {}
        self._ids = count(1)
        self._lock = Lock()

    def criar(self, nome: str, semestre: str | None, turma: str | None, versoes: list[Versao]) -> Avaliacao:
        with self._lock:
            armazenadas = [VersaoArmazenada(codigo=self._novo_codigo(), versao=v) for v in versoes]
            avaliacao = Avaliacao(id=next(self._ids), nome=nome, semestre=semestre, turma=turma, versoes=armazenadas)
            self._avaliacoes[avaliacao.id] = avaliacao
            for armazenada in armazenadas:
                self._por_codigo[armazenada.codigo] = (avaliacao, armazenada)
            return avaliacao

    def listar(self) -> list[Avaliacao]:
        return list(self._avaliacoes.values())

    def obter(self, avaliacao_id: int) -> Avaliacao | None:
        return self._avaliacoes.get(avaliacao_id)

    def obter_por_codigo(self, codigo: str) -> tuple[Avaliacao, VersaoArmazenada] | None:
        return self._por_codigo.get(codigo)

    def _novo_codigo(self) -> str:
        while True:
            codigo = secrets.token_urlsafe(9)
            if codigo not in self._por_codigo:
                return codigo


store = AvaliacoesStore()


def get_store() -> AvaliacoesStore:
    return store
