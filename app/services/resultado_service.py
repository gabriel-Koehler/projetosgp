"""Consulta de resultados, estatísticas e relatório Excel (RF41 a RF48)."""

import psycopg
from fastapi import Depends

from app.database.connection import get_conn
from app.models.avaliacao import Avaliacao
from app.models.resultado import Resultado
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.resultado_repository import ResultadoRepository
from app.services import estatisticas, relatorio_excel
from app.services.errors import NaoEncontrado


class ResultadoService:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self.avaliacoes = AvaliacaoRepository(conn)
        self.resultados = ResultadoRepository(conn)

    def _avaliacao(self, professor_id: int, avaliacao_id: int) -> Avaliacao:
        avaliacao = self.avaliacoes.obter(professor_id, avaliacao_id)
        if not avaliacao:
            raise NaoEncontrado("Avaliação não encontrada.")
        return avaliacao

    def listar(self, professor_id: int, avaliacao_id: int) -> list[Resultado]:
        self._avaliacao(professor_id, avaliacao_id)
        return self.resultados.listar(avaliacao_id)

    def obter(self, professor_id: int, resultado_id: int) -> Resultado:
        resultado = self.resultados.obter(professor_id, resultado_id)
        if not resultado:
            raise NaoEncontrado("Resultado não encontrado.")
        return resultado

    def excluir(self, professor_id: int, resultado_id: int) -> None:
        self.obter(professor_id, resultado_id)
        self.resultados.excluir(resultado_id)

    def estatisticas(self, professor_id: int, avaliacao_id: int) -> estatisticas.Estatisticas:
        avaliacao = self._avaliacao(professor_id, avaliacao_id)
        return estatisticas.calcular(
            self.resultados.listar(avaliacao_id),
            self.resultados.questoes_das_versoes(avaliacao_id),
            self.resultados.gabarito_original(avaliacao_id),
            avaliacao.nota_maxima,
        )

    def relatorio_excel(self, professor_id: int, avaliacao_id: int) -> tuple[str, bytes]:
        avaliacao = self._avaliacao(professor_id, avaliacao_id)
        conteudo = relatorio_excel.gerar_relatorio(
            avaliacao.nome, self.resultados.listar(avaliacao_id), self.estatisticas(professor_id, avaliacao_id)
        )
        return avaliacao.nome, conteudo


def get_resultado_service(conn: psycopg.Connection = Depends(get_conn)) -> ResultadoService:
    return ResultadoService(conn)
