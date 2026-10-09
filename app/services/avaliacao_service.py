"""Regras de avaliação: criação com versões e consulta do gabarito pelo aluno."""

from dataclasses import asdict, dataclass

import psycopg
from fastapi import Depends

from app.database.connection import get_conn
from app.models.avaliacao import Avaliacao, ResumoAvaliacao, VersaoAvaliacao, VersaoPorCodigo
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.cadastros_repository import TurmaRepository
from app.repositories.questao_repository import QuestaoRepository
from app.services.errors import AcessoNegado, Conflito, ErroDeNegocio, NaoEncontrado
from app.services.version_builder import ConfiguracaoVersoes, Questao, gerar_versoes, indice_da_letra


@dataclass(frozen=True)
class GabaritoAluno:
    avaliacao: str
    versao: str
    gabarito: dict[int, str]


class AvaliacaoService:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self.repositorio = AvaliacaoRepository(conn)
        self.questoes = QuestaoRepository(conn)
        self.turmas = TurmaRepository(conn)

    def criar(
        self,
        professor_id: int,
        nome: str,
        turma_id: int | None,
        questao_ids: list[int],
        config: ConfiguracaoVersoes,
        nota_maxima: float = 10,
        gabaritos: dict[int, str] | None = None,
    ) -> Avaliacao:
        """RF14 a RF25. Grava avaliação, versões, questões e gabaritos numa transação só."""
        if turma_id is not None and not self.turmas.obter(professor_id, turma_id):
            raise NaoEncontrado("Turma não encontrada.")
        if len(set(questao_ids)) != len(questao_ids):
            raise ErroDeNegocio("A mesma questão foi selecionada mais de uma vez.")

        encontradas = {q.id: q for q in self.questoes.obter_varias(professor_id, questao_ids)}
        faltando = [str(i) for i in questao_ids if i not in encontradas]
        if faltando:
            raise NaoEncontrado(f"Questões não encontradas no banco: {', '.join(faltando)}.")

        # RF16: o professor pode ajustar o gabarito só para esta avaliação.
        gabaritos = {int(k): v.strip().upper() for k, v in (gabaritos or {}).items()}
        for questao_id, correta in gabaritos.items():
            questao = encontradas.get(questao_id)
            if not questao:
                raise ErroDeNegocio(f"A questão {questao_id} do gabarito não foi selecionada.")
            try:
                if indice_da_letra(correta) >= len(questao.alternativas):
                    raise ValueError
            except ValueError as erro:
                raise ErroDeNegocio(f"Gabarito '{correta}' inválido para a questão {questao_id}.") from erro

        selecionadas = [
            Questao(
                id=str(q.id),
                enunciado=q.enunciado,
                alternativas=q.alternativas,
                correta=gabaritos.get(q.id, q.correta),
            )
            for q in (encontradas[i] for i in questao_ids)
        ]
        try:
            versoes = gerar_versoes(selecionadas, config)
        except ValueError as erro:
            raise ErroDeNegocio(str(erro)) from erro

        configuracao = {**asdict(config), "nomenclatura": config.nomenclatura.value}
        with self.conn.transaction():
            avaliacao_id = self.repositorio.criar(
                professor_id,
                nome.strip(),
                turma_id,
                nota_maxima,
                configuracao,
                [(int(q.id), q.correta) for q in selecionadas],
                versoes,
            )
        return self.obter(professor_id, avaliacao_id)

    def listar(self, professor_id: int, turma_id: int | None = None) -> list[ResumoAvaliacao]:
        return self.repositorio.listar(professor_id, turma_id)

    def obter(self, professor_id: int, avaliacao_id: int) -> Avaliacao:
        avaliacao = self.repositorio.obter(professor_id, avaliacao_id)
        if not avaliacao:
            raise NaoEncontrado("Avaliação não encontrada.")
        return avaliacao

    def obter_versao(self, professor_id: int, avaliacao_id: int, codigo: str) -> VersaoAvaliacao:
        for versao in self.obter(professor_id, avaliacao_id).versoes:
            if versao.codigo == codigo:
                return versao
        raise NaoEncontrado("Versão não encontrada.")

    def liberar_gabarito(self, professor_id: int, avaliacao_id: int, liberado: bool) -> Avaliacao:
        if not self.repositorio.definir_gabarito_liberado(professor_id, avaliacao_id, liberado):
            raise NaoEncontrado("Avaliação não encontrada.")
        return self.obter(professor_id, avaliacao_id)

    def excluir(self, professor_id: int, avaliacao_id: int) -> None:
        self.obter(professor_id, avaliacao_id)
        if self.repositorio.tem_resultados(avaliacao_id):
            raise Conflito("A avaliação já tem provas corrigidas e não pode ser excluída.")
        self.repositorio.excluir(avaliacao_id)

    def versao_por_codigo(self, codigo: str) -> VersaoPorCodigo:
        versao = self.repositorio.obter_por_codigo(codigo)
        if not versao:
            raise NaoEncontrado("Gabarito não encontrado. Confira o QR Code.")
        return versao

    def gabarito_do_aluno(self, codigo: str) -> GabaritoAluno:
        """Consulta pelo QR Code (RF29, RF30): só nomes e letras corretas."""
        versao = self.versao_por_codigo(codigo)
        if not versao.gabarito_liberado:
            raise AcessoNegado("O gabarito desta prova ainda não foi liberado pelo professor.")
        return GabaritoAluno(avaliacao=versao.avaliacao_nome, versao=versao.versao_nome, gabarito=versao.gabarito)


def get_avaliacao_service(conn: psycopg.Connection = Depends(get_conn)) -> AvaliacaoService:
    return AvaliacaoService(conn)
