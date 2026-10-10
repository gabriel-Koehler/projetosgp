"""Regras de semestres (RF02), turmas (RF03) e alunos (RF04, RF05)."""

from datetime import date

import psycopg
from fastapi import Depends

from app.database.connection import get_conn
from app.models.cadastros import Aluno, Semestre, Turma
from app.repositories.cadastros_repository import AlunoRepository, SemestreRepository, TurmaRepository
from app.services import importacao
from app.services.errors import Conflito, ErroDeNegocio, NaoEncontrado


def _validar_datas(data_inicio: date | None, data_fim: date | None) -> None:
    if data_inicio and data_fim and data_fim < data_inicio:
        raise ErroDeNegocio("A data de fim deve ser depois da data de início.")


class CadastrosService:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn
        self.semestres = SemestreRepository(conn)
        self.turmas = TurmaRepository(conn)
        self.alunos = AlunoRepository(conn)

    # --- Semestres -------------------------------------------------------------

    def listar_semestres(self, professor_id: int, ativo: bool | None = None) -> list[Semestre]:
        return self.semestres.listar(professor_id, ativo)

    def obter_semestre(self, professor_id: int, semestre_id: int) -> Semestre:
        semestre = self.semestres.obter(professor_id, semestre_id)
        if not semestre:
            raise NaoEncontrado("Semestre não encontrado.")
        return semestre

    def criar_semestre(self, professor_id: int, nome: str, data_inicio=None, data_fim=None) -> Semestre:
        _validar_datas(data_inicio, data_fim)
        try:
            return self.semestres.criar(professor_id, nome.strip(), data_inicio, data_fim)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"Já existe um semestre chamado '{nome}'.") from erro

    def atualizar_semestre(self, professor_id: int, semestre_id: int, nome: str, data_inicio=None, data_fim=None):
        _validar_datas(data_inicio, data_fim)
        try:
            semestre = self.semestres.atualizar(professor_id, semestre_id, nome.strip(), data_inicio, data_fim)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"Já existe um semestre chamado '{nome}'.") from erro
        if not semestre:
            raise NaoEncontrado("Semestre não encontrado.")
        return semestre

    def definir_semestre_ativo(self, professor_id: int, semestre_id: int, ativo: bool) -> Semestre:
        semestre = self.semestres.definir_ativo(professor_id, semestre_id, ativo)
        if not semestre:
            raise NaoEncontrado("Semestre não encontrado.")
        return semestre

    # --- Turmas ----------------------------------------------------------------

    def listar_turmas(self, professor_id: int, semestre_id: int | None = None) -> list[Turma]:
        return self.turmas.listar(professor_id, semestre_id)

    def obter_turma(self, professor_id: int, turma_id: int) -> Turma:
        turma = self.turmas.obter(professor_id, turma_id)
        if not turma:
            raise NaoEncontrado("Turma não encontrada.")
        return turma

    def criar_turma(self, professor_id: int, semestre_id: int, nome: str, disciplina: str | None = None) -> Turma:
        self.obter_semestre(professor_id, semestre_id)
        try:
            turma_id = self.turmas.criar(semestre_id, nome.strip(), disciplina)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"Já existe a turma '{nome}' neste semestre.") from erro
        return self.obter_turma(professor_id, turma_id)

    def atualizar_turma(self, professor_id: int, turma_id: int, semestre_id: int, nome: str, disciplina=None) -> Turma:
        self.obter_turma(professor_id, turma_id)
        self.obter_semestre(professor_id, semestre_id)
        try:
            self.turmas.atualizar(turma_id, semestre_id, nome.strip(), disciplina)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"Já existe a turma '{nome}' neste semestre.") from erro
        return self.obter_turma(professor_id, turma_id)

    def excluir_turma(self, professor_id: int, turma_id: int) -> None:
        self.obter_turma(professor_id, turma_id)
        try:
            self.turmas.excluir(turma_id)
        except psycopg.errors.ForeignKeyViolation as erro:
            raise Conflito("A turma tem alunos ou avaliações e não pode ser excluída.") from erro

    # --- Alunos ----------------------------------------------------------------

    def listar_alunos(self, professor_id: int, turma_id: int) -> list[Aluno]:
        self.obter_turma(professor_id, turma_id)
        return self.alunos.listar(turma_id)

    def obter_aluno(self, professor_id: int, aluno_id: int) -> Aluno:
        aluno = self.alunos.obter(professor_id, aluno_id)
        if not aluno:
            raise NaoEncontrado("Aluno não encontrado.")
        return aluno

    def criar_aluno(self, professor_id: int, turma_id: int, nome: str, matricula: str, email: str | None) -> Aluno:
        self.obter_turma(professor_id, turma_id)
        try:
            return self.alunos.criar(turma_id, nome.strip(), matricula.strip(), email)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"A matrícula {matricula} já está cadastrada nesta turma.") from erro

    def atualizar_aluno(self, professor_id: int, aluno_id: int, nome: str, matricula: str, email: str | None) -> Aluno:
        self.obter_aluno(professor_id, aluno_id)
        try:
            self.alunos.atualizar(aluno_id, nome.strip(), matricula.strip(), email)
        except psycopg.errors.UniqueViolation as erro:
            raise Conflito(f"A matrícula {matricula} já está cadastrada nesta turma.") from erro
        return self.obter_aluno(professor_id, aluno_id)

    def excluir_aluno(self, professor_id: int, aluno_id: int) -> None:
        # Resultados já registrados continuam, sem o vínculo com o aluno.
        self.obter_aluno(professor_id, aluno_id)
        self.alunos.excluir(aluno_id)

    def importar_alunos(
        self, professor_id: int, turma_id: int, conteudo: bytes, nome_arquivo: str, confirmar: bool
    ) -> tuple[importacao.Previa, int]:
        """RF05: sem confirmar, só devolve a prévia; confirmando, grava as linhas válidas."""
        self.obter_turma(professor_id, turma_id)
        linhas = importacao.ler_planilha(conteudo, nome_arquivo)
        previa = importacao.validar_alunos(linhas, self.alunos.matriculas(turma_id))
        importados = 0
        if confirmar and previa.validas:
            with self.conn.transaction():
                importados = self.alunos.criar_varios(
                    turma_id, [(l.dados["nome"], l.dados["matricula"], l.dados["email"]) for l in previa.validas]
                )
        return previa, importados


def get_cadastros_service(conn: psycopg.Connection = Depends(get_conn)) -> CadastrosService:
    return CadastrosService(conn)
