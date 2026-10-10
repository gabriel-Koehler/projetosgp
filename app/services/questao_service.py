"""Regras do banco de questões (RF06 a RF13, RN12, RN13)."""

from dataclasses import dataclass

import psycopg
from fastapi import Depends

from app.database.connection import get_conn
from app.models.cadastros import QuestaoBanco
from app.repositories.questao_repository import QuestaoRepository
from app.services import importacao
from app.services.errors import ErroDeNegocio, NaoEncontrado
from app.services.version_builder import indice_da_letra


@dataclass(frozen=True)
class ResultadoExclusao:
    excluida: bool
    arquivada: bool
    mensagem: str


def validar_questao(dados: dict) -> dict:
    alternativas = [a.strip() for a in dados["alternativas"]]
    if any(not a for a in alternativas):
        raise ErroDeNegocio("As alternativas não podem ficar em branco.")
    if len({importacao.normalizar_texto(a) for a in alternativas}) != len(alternativas):
        raise ErroDeNegocio("Há alternativas repetidas.")
    correta = dados["correta"].strip().upper()
    try:
        if indice_da_letra(correta) >= len(alternativas):
            raise ValueError
    except ValueError as erro:
        raise ErroDeNegocio(f"O gabarito '{correta}' não corresponde a nenhuma alternativa.") from erro
    return {**dados, "enunciado": dados["enunciado"].strip(), "alternativas": alternativas, "correta": correta}


class QuestaoService:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self.repositorio = QuestaoRepository(conn)

    def buscar(self, professor_id: int, pagina: int = 1, por_pagina: int = 50, **filtros) -> tuple[list[QuestaoBanco], int]:
        return self.repositorio.buscar(professor_id, limite=por_pagina, deslocamento=(pagina - 1) * por_pagina, **filtros)

    def filtros(self, professor_id: int) -> dict[str, list[str]]:
        return self.repositorio.filtros(professor_id)

    def obter(self, professor_id: int, questao_id: int) -> QuestaoBanco:
        questao = self.repositorio.obter(professor_id, questao_id)
        if not questao:
            raise NaoEncontrado("Questão não encontrada.")
        return questao

    def criar(self, professor_id: int, dados: dict) -> QuestaoBanco:
        dados = validar_questao(dados)
        with self.conn.transaction():
            questao_id = self.repositorio.criar(professor_id, dados)
        return self.obter(professor_id, questao_id)

    def atualizar(self, professor_id: int, questao_id: int, dados: dict) -> QuestaoBanco:
        """RF07. Provas já geradas guardam uma cópia da questão (RN14): não mudam."""
        self.obter(professor_id, questao_id)
        dados = validar_questao(dados)
        with self.conn.transaction():
            self.repositorio.atualizar(questao_id, dados)
        return self.obter(professor_id, questao_id)

    def excluir(self, professor_id: int, questao_id: int) -> ResultadoExclusao:
        """RF08: questão já usada em avaliação é arquivada (some do banco, mas o histórico fica)."""
        self.obter(professor_id, questao_id)
        if self.repositorio.usada_em_avaliacao(questao_id):
            self.repositorio.arquivar(questao_id)
            return ResultadoExclusao(
                excluida=False,
                arquivada=True,
                mensagem="A questão já foi usada em avaliações: ela saiu do banco, mas o histórico foi mantido.",
            )
        self.repositorio.excluir(questao_id)
        return ResultadoExclusao(excluida=True, arquivada=False, mensagem="Questão excluída.")

    def importar(
        self, professor_id: int, conteudo: bytes, nome_arquivo: str, confirmar: bool
    ) -> tuple[importacao.Previa, int]:
        """RF10 a RF12: sem confirmar, só devolve a prévia; confirmando, grava as linhas válidas."""
        linhas = importacao.ler_planilha(conteudo, nome_arquivo)
        previa = importacao.validar_questoes(linhas, self.repositorio.enunciados(professor_id))
        importadas = 0
        if confirmar and previa.validas:
            with self.conn.transaction():
                for linha in previa.validas:
                    self.repositorio.criar(professor_id, linha.dados)
                    importadas += 1
        return previa, importadas


def get_questao_service(conn: psycopg.Connection = Depends(get_conn)) -> QuestaoService:
    return QuestaoService(conn)
