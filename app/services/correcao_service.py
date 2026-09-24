"""Correção das folhas de resposta: leitura automática (OMR) da foto enviada pelo professor."""

from dataclasses import dataclass

import psycopg
from fastapi import Depends

from app.database.connection import get_conn
from app.models.avaliacao import VersaoPorCodigo
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.services import omr_service
from app.services.errors import ErroDeNegocio
from app.services.omr_service import ErroLeitura, LeituraFolha

TAMANHO_MAXIMO_FOTO = 15 * 1024 * 1024  # 15 MB


class LeituraInvalida(ErroDeNegocio):
    """Folha que não pôde ser lida (RF36, RF40): nada é registrado."""

    def __init__(self, erro: ErroLeitura) -> None:
        super().__init__(erro.mensagem)
        self.codigo = erro.codigo


@dataclass
class LeituraCompleta:
    leitura: LeituraFolha
    versao: VersaoPorCodigo


class CorrecaoService:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self.avaliacoes = AvaliacaoRepository(conn)

    def ler_folha(self, professor_id: int, conteudo: bytes) -> LeituraCompleta:
        """RF32 a RF36: identifica a versão pelo QR Code e lê as respostas marcadas."""
        if len(conteudo) > TAMANHO_MAXIMO_FOTO:
            raise ErroDeNegocio("Imagem muito grande (máximo 15 MB).")

        encontrada: dict[str, VersaoPorCodigo] = {}

        def alternativas_da_versao(codigo: str) -> dict[int, int]:
            versao = self.avaliacoes.obter_por_codigo(codigo)
            if versao is None or versao.professor_id != professor_id:
                raise ErroLeitura(
                    "prova_desconhecida",
                    "O QR Code desta folha não é de nenhuma das suas avaliações. Confira se é a folha certa.",
                )
            encontrada["versao"] = versao
            return versao.alternativas_por_questao

        try:
            leitura = omr_service.ler_folha(conteudo, alternativas_da_versao)
        except ErroLeitura as erro:
            raise LeituraInvalida(erro) from erro
        return LeituraCompleta(leitura=leitura, versao=encontrada["versao"])


def get_correcao_service(conn: psycopg.Connection = Depends(get_conn)) -> CorrecaoService:
    return CorrecaoService(conn)
