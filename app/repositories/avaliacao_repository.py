"""Acesso aos dados de avaliações.

Implementação em memória (dados da N1). A persistência no Supabase entra no [N2-BE-04].
"""

import secrets
from itertools import count
from threading import Lock

from app.models.avaliacao import Avaliacao, VersaoAvaliacao
from app.services.version_builder import Versao


def novo_codigo() -> str:
    return secrets.token_urlsafe(9)


class AvaliacaoRepository:
    def __init__(self) -> None:
        self._avaliacoes: dict[int, Avaliacao] = {}
        self._por_codigo: dict[str, tuple[Avaliacao, VersaoAvaliacao]] = {}
        self._ids = count(1)
        self._lock = Lock()

    def criar(self, nome: str, semestre: str | None, turma: str | None, versoes: list[Versao]) -> Avaliacao:
        with self._lock:
            armazenadas = [VersaoAvaliacao(codigo=self._codigo_livre(), versao=v) for v in versoes]
            avaliacao = Avaliacao(id=next(self._ids), nome=nome, semestre=semestre, turma=turma, versoes=armazenadas)
            self._avaliacoes[avaliacao.id] = avaliacao
            for armazenada in armazenadas:
                self._por_codigo[armazenada.codigo] = (avaliacao, armazenada)
            return avaliacao

    def listar(self) -> list[Avaliacao]:
        return list(self._avaliacoes.values())

    def obter(self, avaliacao_id: int) -> Avaliacao | None:
        return self._avaliacoes.get(avaliacao_id)

    def obter_por_codigo(self, codigo: str) -> tuple[Avaliacao, VersaoAvaliacao] | None:
        return self._por_codigo.get(codigo)

    def definir_gabarito_liberado(self, avaliacao_id: int, liberado: bool) -> None:
        self._avaliacoes[avaliacao_id].gabarito_liberado = liberado

    def _codigo_livre(self) -> str:
        while (codigo := novo_codigo()) in self._por_codigo:
            pass
        return codigo


_repositorio = AvaliacaoRepository()


def get_avaliacao_repository() -> AvaliacaoRepository:
    return _repositorio
