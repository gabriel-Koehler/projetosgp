"""Consultas SQL do banco de questões (RF06 a RF13)."""

import psycopg

from app.models.cadastros import QuestaoBanco
from app.services.version_builder import letra

SELECT = """
    SELECT q.id, q.enunciado, q.correta, q.disciplina, q.categoria, q.dificuldade, q.arquivada,
           q.criado_em, q.atualizado_em,
           COALESCE(
               (SELECT json_agg(a.texto ORDER BY a.letra) FROM alternativa a WHERE a.questao_id = q.id),
               '[]'::json
           ) AS alternativas
    FROM questao q
"""


def _questao(linha: dict) -> QuestaoBanco:
    return QuestaoBanco(**linha)


class QuestaoRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def buscar(
        self,
        professor_id: int,
        texto: str | None = None,
        disciplina: str | None = None,
        categoria: str | None = None,
        dificuldade: str | None = None,
        limite: int = 50,
        deslocamento: int = 0,
    ) -> tuple[list[QuestaoBanco], int]:
        filtros = ["q.professor_id = %(professor)s", "NOT q.arquivada"]
        parametros: dict = {"professor": professor_id, "limite": limite, "deslocamento": deslocamento}
        if texto:
            filtros.append(
                "(q.enunciado ILIKE %(texto)s OR EXISTS "
                "(SELECT 1 FROM alternativa a WHERE a.questao_id = q.id AND a.texto ILIKE %(texto)s))"
            )
            parametros["texto"] = f"%{texto}%"
        for campo, valor in (("disciplina", disciplina), ("categoria", categoria), ("dificuldade", dificuldade)):
            if valor:
                filtros.append(f"q.{campo} = %({campo})s")
                parametros[campo] = valor
        where = " WHERE " + " AND ".join(filtros)

        total = self.conn.execute("SELECT count(*) AS n FROM questao q" + where, parametros).fetchone()["n"]
        linhas = self.conn.execute(
            SELECT + where + " ORDER BY q.id DESC LIMIT %(limite)s OFFSET %(deslocamento)s", parametros
        ).fetchall()
        return [_questao(l) for l in linhas], total

    def obter(self, professor_id: int, questao_id: int) -> QuestaoBanco | None:
        linha = self.conn.execute(
            SELECT + " WHERE q.professor_id = %s AND q.id = %s AND NOT q.arquivada", (professor_id, questao_id)
        ).fetchone()
        return _questao(linha) if linha else None

    def obter_varias(self, professor_id: int, ids: list[int]) -> list[QuestaoBanco]:
        linhas = self.conn.execute(
            SELECT + " WHERE q.professor_id = %s AND q.id = ANY(%s) AND NOT q.arquivada", (professor_id, ids)
        ).fetchall()
        return [_questao(l) for l in linhas]

    def filtros(self, professor_id: int) -> dict[str, list[str]]:
        resultado = {}
        for campo in ("disciplina", "categoria"):
            linhas = self.conn.execute(
                f"""
                SELECT DISTINCT {campo} AS v FROM questao
                WHERE professor_id = %s AND NOT arquivada AND {campo} IS NOT NULL ORDER BY 1
                """,
                (professor_id,),
            ).fetchall()
            resultado[campo] = [l["v"] for l in linhas]
        return resultado

    def enunciados(self, professor_id: int) -> list[str]:
        linhas = self.conn.execute(
            "SELECT enunciado FROM questao WHERE professor_id = %s AND NOT arquivada", (professor_id,)
        ).fetchall()
        return [l["enunciado"] for l in linhas]

    def criar(self, professor_id: int, dados: dict) -> int:
        questao_id = self.conn.execute(
            """
            INSERT INTO questao (professor_id, enunciado, correta, disciplina, categoria, dificuldade)
            VALUES (%(professor)s, %(enunciado)s, %(correta)s, %(disciplina)s, %(categoria)s, %(dificuldade)s)
            RETURNING id
            """,
            {"professor": professor_id, **dados},
        ).fetchone()["id"]
        self._gravar_alternativas(questao_id, dados["alternativas"])
        return questao_id

    def atualizar(self, questao_id: int, dados: dict) -> None:
        self.conn.execute(
            """
            UPDATE questao SET enunciado = %(enunciado)s, correta = %(correta)s, disciplina = %(disciplina)s,
                   categoria = %(categoria)s, dificuldade = %(dificuldade)s, atualizado_em = now()
            WHERE id = %(id)s
            """,
            {"id": questao_id, **dados},
        )
        self.conn.execute("DELETE FROM alternativa WHERE questao_id = %s", (questao_id,))
        self._gravar_alternativas(questao_id, dados["alternativas"])

    def usada_em_avaliacao(self, questao_id: int) -> bool:
        return self.conn.execute(
            "SELECT EXISTS (SELECT 1 FROM avaliacao_questao WHERE questao_id = %s) AS usada", (questao_id,)
        ).fetchone()["usada"]

    def arquivar(self, questao_id: int) -> None:
        self.conn.execute("UPDATE questao SET arquivada = TRUE, atualizado_em = now() WHERE id = %s", (questao_id,))

    def excluir(self, questao_id: int) -> None:
        self.conn.execute("DELETE FROM questao WHERE id = %s", (questao_id,))

    def _gravar_alternativas(self, questao_id: int, alternativas: list[str]) -> None:
        with self.conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO alternativa (questao_id, letra, texto) VALUES (%s, %s, %s)",
                [(questao_id, letra(i), texto) for i, texto in enumerate(alternativas)],
            )
