"""Regras de avaliação: criação com versões e consulta do gabarito pelo aluno."""

from dataclasses import dataclass

from fastapi import Depends

from app.models.avaliacao import Avaliacao, VersaoAvaliacao
from app.repositories.avaliacao_repository import AvaliacaoRepository, get_avaliacao_repository
from app.services.errors import AcessoNegado, ErroDeNegocio, NaoEncontrado
from app.services.version_builder import ConfiguracaoVersoes, Questao, gerar_versoes


@dataclass(frozen=True)
class GabaritoAluno:
    avaliacao: str
    versao: str
    gabarito: dict[int, str]


class AvaliacaoService:
    def __init__(self, repositorio: AvaliacaoRepository) -> None:
        self.repositorio = repositorio

    def criar(
        self,
        nome: str,
        semestre: str | None,
        turma: str | None,
        questoes: list[Questao],
        config: ConfiguracaoVersoes,
    ) -> Avaliacao:
        try:
            versoes = gerar_versoes(questoes, config)
        except ValueError as erro:
            raise ErroDeNegocio(str(erro)) from erro
        return self.repositorio.criar(nome, semestre, turma, versoes)

    def listar(self) -> list[Avaliacao]:
        return self.repositorio.listar()

    def obter(self, avaliacao_id: int) -> Avaliacao:
        avaliacao = self.repositorio.obter(avaliacao_id)
        if not avaliacao:
            raise NaoEncontrado("Avaliação não encontrada.")
        return avaliacao

    def obter_versao(self, avaliacao_id: int, codigo: str) -> VersaoAvaliacao:
        for versao in self.obter(avaliacao_id).versoes:
            if versao.codigo == codigo:
                return versao
        raise NaoEncontrado("Versão não encontrada.")

    def liberar_gabarito(self, avaliacao_id: int, liberado: bool) -> Avaliacao:
        self.obter(avaliacao_id)
        self.repositorio.definir_gabarito_liberado(avaliacao_id, liberado)
        return self.obter(avaliacao_id)

    def gabarito_do_aluno(self, codigo: str) -> GabaritoAluno:
        """Consulta pelo QR Code (RF29, RF30): só nomes e letras corretas."""
        encontrado = self.repositorio.obter_por_codigo(codigo)
        if not encontrado:
            raise NaoEncontrado("Gabarito não encontrado. Confira o QR Code.")
        avaliacao, versao = encontrado
        if not avaliacao.gabarito_liberado:
            raise AcessoNegado("O gabarito desta prova ainda não foi liberado pelo professor.")
        return GabaritoAluno(avaliacao=avaliacao.nome, versao=versao.versao.nome, gabarito=versao.versao.gabarito)


def get_avaliacao_service(
    repositorio: AvaliacaoRepository = Depends(get_avaliacao_repository),
) -> AvaliacaoService:
    return AvaliacaoService(repositorio)
