"""Consultas SQL de professor, semestre, turma e aluno.

Todas as consultas filtram pelo professor dono dos dados: um professor nunca
enxerga semestres, turmas ou alunos de outro.
"""

import psycopg

from app.models.cadastros import Aluno, Professor, Semestre, Turma


class ProfessorRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def obter_por_username(self, username: str) -> Professor | None:
        linha = self.conn.execute(
            "SELECT id, username, nome, senha_hash FROM professor WHERE username = %s", (username,)
        ).fetchone()
        return Professor(**linha) if linha else None


class SemestreRepository:
    COLUNAS = "id, nome, data_inicio, data_fim, ativo"

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def listar(self, professor_id: int, ativo: bool | None = None) -> list[Semestre]:
        linhas = self.conn.execute(
            f"""
            SELECT {self.COLUNAS} FROM semestre
            WHERE professor_id = %s AND (%s::boolean IS NULL OR ativo = %s)
            ORDER BY data_inicio DESC NULLS LAST, nome DESC
            """,
            (professor_id, ativo, ativo),
        ).fetchall()
        return [Semestre(**l) for l in linhas]

    def obter(self, professor_id: int, semestre_id: int) -> Semestre | None:
        linha = self.conn.execute(
            f"SELECT {self.COLUNAS} FROM semestre WHERE professor_id = %s AND id = %s", (professor_id, semestre_id)
        ).fetchone()
        return Semestre(**linha) if linha else None

    def criar(self, professor_id: int, nome: str, data_inicio, data_fim) -> Semestre:
        linha = self.conn.execute(
            f"""
            INSERT INTO semestre (professor_id, nome, data_inicio, data_fim)
            VALUES (%s, %s, %s, %s) RETURNING {self.COLUNAS}
            """,
            (professor_id, nome, data_inicio, data_fim),
        ).fetchone()
        return Semestre(**linha)

    def atualizar(self, professor_id: int, semestre_id: int, nome: str, data_inicio, data_fim) -> Semestre | None:
        linha = self.conn.execute(
            f"""
            UPDATE semestre SET nome = %s, data_inicio = %s, data_fim = %s
            WHERE professor_id = %s AND id = %s RETURNING {self.COLUNAS}
            """,
            (nome, data_inicio, data_fim, professor_id, semestre_id),
        ).fetchone()
        return Semestre(**linha) if linha else None

    def definir_ativo(self, professor_id: int, semestre_id: int, ativo: bool) -> Semestre | None:
        linha = self.conn.execute(
            f"UPDATE semestre SET ativo = %s WHERE professor_id = %s AND id = %s RETURNING {self.COLUNAS}",
            (ativo, professor_id, semestre_id),
        ).fetchone()
        return Semestre(**linha) if linha else None


class TurmaRepository:
    SELECT = """
        SELECT t.id, t.semestre_id, s.nome AS semestre_nome, t.nome, t.disciplina
        FROM turma t JOIN semestre s ON s.id = t.semestre_id
        WHERE s.professor_id = %s
    """

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def listar(self, professor_id: int, semestre_id: int | None = None) -> list[Turma]:
        linhas = self.conn.execute(
            self.SELECT + " AND (%s::bigint IS NULL OR t.semestre_id = %s) ORDER BY s.nome DESC, t.nome",
            (professor_id, semestre_id, semestre_id),
        ).fetchall()
        return [Turma(**l) for l in linhas]

    def obter(self, professor_id: int, turma_id: int) -> Turma | None:
        linha = self.conn.execute(self.SELECT + " AND t.id = %s", (professor_id, turma_id)).fetchone()
        return Turma(**linha) if linha else None

    def criar(self, semestre_id: int, nome: str, disciplina: str | None) -> int:
        return self.conn.execute(
            "INSERT INTO turma (semestre_id, nome, disciplina) VALUES (%s, %s, %s) RETURNING id",
            (semestre_id, nome, disciplina),
        ).fetchone()["id"]

    def atualizar(self, turma_id: int, semestre_id: int, nome: str, disciplina: str | None) -> None:
        self.conn.execute(
            "UPDATE turma SET semestre_id = %s, nome = %s, disciplina = %s WHERE id = %s",
            (semestre_id, nome, disciplina, turma_id),
        )

    def excluir(self, turma_id: int) -> None:
        self.conn.execute("DELETE FROM turma WHERE id = %s", (turma_id,))


class AlunoRepository:
    COLUNAS = "id, turma_id, nome, matricula, email"

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def listar(self, turma_id: int) -> list[Aluno]:
        linhas = self.conn.execute(
            f"SELECT {self.COLUNAS} FROM aluno WHERE turma_id = %s ORDER BY nome", (turma_id,)
        ).fetchall()
        return [Aluno(**l) for l in linhas]

    def obter(self, professor_id: int, aluno_id: int) -> Aluno | None:
        linha = self.conn.execute(
            """
            SELECT a.id, a.turma_id, a.nome, a.matricula, a.email
            FROM aluno a JOIN turma t ON t.id = a.turma_id JOIN semestre s ON s.id = t.semestre_id
            WHERE s.professor_id = %s AND a.id = %s
            """,
            (professor_id, aluno_id),
        ).fetchone()
        return Aluno(**linha) if linha else None

    def matriculas(self, turma_id: int) -> set[str]:
        linhas = self.conn.execute("SELECT matricula FROM aluno WHERE turma_id = %s", (turma_id,)).fetchall()
        return {l["matricula"] for l in linhas}

    def criar(self, turma_id: int, nome: str, matricula: str, email: str | None) -> Aluno:
        linha = self.conn.execute(
            f"""
            INSERT INTO aluno (turma_id, nome, matricula, email)
            VALUES (%s, %s, %s, %s) RETURNING {self.COLUNAS}
            """,
            (turma_id, nome, matricula, email),
        ).fetchone()
        return Aluno(**linha)

    def criar_varios(self, turma_id: int, alunos: list[tuple[str, str, str | None]]) -> int:
        with self.conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO aluno (turma_id, nome, matricula, email) VALUES (%s, %s, %s, %s)",
                [(turma_id, nome, matricula, email) for nome, matricula, email in alunos],
            )
        return len(alunos)

    def atualizar(self, aluno_id: int, nome: str, matricula: str, email: str | None) -> None:
        self.conn.execute(
            "UPDATE aluno SET nome = %s, matricula = %s, email = %s WHERE id = %s", (nome, matricula, email, aluno_id)
        )

    def excluir(self, aluno_id: int) -> None:
        self.conn.execute("DELETE FROM aluno WHERE id = %s", (aluno_id,))
