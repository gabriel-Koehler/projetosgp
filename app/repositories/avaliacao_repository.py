"""Consultas SQL de avaliações, versões e gabaritos (RF14 a RF25).

Os métodos de gravação não abrem transação sozinhos: quem chama (o service)
envolve tudo em `with conn.transaction():` para gravar a avaliação inteira ou nada.
"""

import secrets

import psycopg
from psycopg.types.json import Jsonb

from app.models.avaliacao import Avaliacao, ResumoAvaliacao, VersaoAvaliacao, VersaoPorCodigo
from app.services.version_builder import QuestaoVersao, Versao

SELECT_AVALIACAO = """
    SELECT a.id, a.nome, a.turma_id, t.nome AS turma_nome, s.nome AS semestre_nome,
           a.nota_maxima::float AS nota_maxima, a.configuracao, a.gabarito_liberado, a.criada_em
    FROM avaliacao a
    LEFT JOIN turma t ON t.id = a.turma_id
    LEFT JOIN semestre s ON s.id = t.semestre_id
"""


def novo_codigo() -> str:
    return secrets.token_urlsafe(9)


class AvaliacaoRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    # --- Gravação ------------------------------------------------------------------

    def criar(
        self,
        professor_id: int,
        nome: str,
        turma_id: int | None,
        nota_maxima: float,
        configuracao: dict,
        selecionadas: list[tuple[int, str]],  # (questao_id, correta) na ordem escolhida
        versoes: list[Versao],
    ) -> int:
        avaliacao_id = self.conn.execute(
            """
            INSERT INTO avaliacao (professor_id, turma_id, nome, nota_maxima, configuracao)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (professor_id, turma_id, nome, nota_maxima, Jsonb(configuracao)),
        ).fetchone()["id"]

        with self.conn.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO avaliacao_questao (avaliacao_id, questao_id, ordem, correta) VALUES (%s, %s, %s, %s)",
                [(avaliacao_id, qid, ordem, correta) for ordem, (qid, correta) in enumerate(selecionadas, start=1)],
            )
            for ordem, versao in enumerate(versoes, start=1):
                versao_id = cursor.execute(
                    "INSERT INTO versao_avaliacao (avaliacao_id, nome, codigo, ordem) VALUES (%s, %s, %s, %s) RETURNING id",
                    (avaliacao_id, versao.nome, novo_codigo(), ordem),
                ).fetchone()["id"]
                cursor.executemany(
                    """
                    INSERT INTO questao_versao (versao_id, numero, questao_id, enunciado, alternativas, ordem_original)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [
                        (versao_id, q.numero, int(q.questao_id), q.enunciado, Jsonb(q.alternativas), Jsonb(q.ordem_original))
                        for q in versao.questoes
                    ],
                )
                cursor.executemany(
                    "INSERT INTO gabarito_versao (versao_id, numero, correta) VALUES (%s, %s, %s)",
                    [(versao_id, numero, correta) for numero, correta in versao.gabarito.items()],
                )
        return avaliacao_id

    def definir_gabarito_liberado(self, professor_id: int, avaliacao_id: int, liberado: bool) -> bool:
        cursor = self.conn.execute(
            "UPDATE avaliacao SET gabarito_liberado = %s WHERE professor_id = %s AND id = %s",
            (liberado, professor_id, avaliacao_id),
        )
        return cursor.rowcount == 1

    def tem_resultados(self, avaliacao_id: int) -> bool:
        return self.conn.execute(
            "SELECT EXISTS (SELECT 1 FROM resultado_correcao WHERE avaliacao_id = %s) AS tem", (avaliacao_id,)
        ).fetchone()["tem"]

    def excluir(self, avaliacao_id: int) -> None:
        self.conn.execute("DELETE FROM avaliacao WHERE id = %s", (avaliacao_id,))

    # --- Consulta ------------------------------------------------------------------

    def listar(self, professor_id: int, turma_id: int | None = None) -> list[ResumoAvaliacao]:
        linhas = self.conn.execute(
            """
            SELECT a.id, a.nome, a.turma_id, t.nome AS turma_nome, s.nome AS semestre_nome,
                   a.nota_maxima::float AS nota_maxima, a.gabarito_liberado, a.criada_em,
                   (SELECT count(*) FROM versao_avaliacao v WHERE v.avaliacao_id = a.id) AS quantidade_versoes,
                   (SELECT count(*) FROM avaliacao_questao q WHERE q.avaliacao_id = a.id) AS quantidade_questoes
            FROM avaliacao a
            LEFT JOIN turma t ON t.id = a.turma_id
            LEFT JOIN semestre s ON s.id = t.semestre_id
            WHERE a.professor_id = %s AND (%s::bigint IS NULL OR a.turma_id = %s)
            ORDER BY a.criada_em DESC, a.id DESC
            """,
            (professor_id, turma_id, turma_id),
        ).fetchall()
        return [ResumoAvaliacao(**l) for l in linhas]

    def obter(self, professor_id: int, avaliacao_id: int) -> Avaliacao | None:
        linha = self.conn.execute(
            SELECT_AVALIACAO + " WHERE a.professor_id = %s AND a.id = %s", (professor_id, avaliacao_id)
        ).fetchone()
        if not linha:
            return None
        avaliacao = Avaliacao(**linha)
        avaliacao.versoes = self._versoes(avaliacao_id)
        return avaliacao

    def _versoes(self, avaliacao_id: int) -> list[VersaoAvaliacao]:
        linhas = self.conn.execute(
            """
            SELECT v.id AS versao_id, v.nome AS versao_nome, v.codigo,
                   q.numero, q.questao_id, q.enunciado, q.alternativas, q.ordem_original, g.correta
            FROM versao_avaliacao v
            JOIN questao_versao q ON q.versao_id = v.id
            JOIN gabarito_versao g ON g.versao_id = v.id AND g.numero = q.numero
            WHERE v.avaliacao_id = %s
            ORDER BY v.ordem, q.numero
            """,
            (avaliacao_id,),
        ).fetchall()

        versoes: dict[int, VersaoAvaliacao] = {}
        for l in linhas:
            if l["versao_id"] not in versoes:
                versoes[l["versao_id"]] = VersaoAvaliacao(
                    id=l["versao_id"], codigo=l["codigo"], versao=Versao(nome=l["versao_nome"], questoes=[])
                )
            versoes[l["versao_id"]].versao.questoes.append(
                QuestaoVersao(
                    numero=l["numero"],
                    questao_id=str(l["questao_id"]) if l["questao_id"] is not None else None,
                    enunciado=l["enunciado"],
                    alternativas=l["alternativas"],
                    correta=l["correta"],
                    ordem_original=l["ordem_original"],
                )
            )
        return list(versoes.values())

    def obter_por_codigo(self, codigo: str) -> VersaoPorCodigo | None:
        linha = self.conn.execute(
            """
            SELECT a.id AS avaliacao_id, a.professor_id, a.nome AS avaliacao_nome, a.gabarito_liberado,
                   a.nota_maxima::float AS nota_maxima, v.id AS versao_id, v.nome AS versao_nome,
                   (SELECT json_object_agg(g.numero, g.correta ORDER BY g.numero)
                      FROM gabarito_versao g WHERE g.versao_id = v.id) AS gabarito,
                   (SELECT json_object_agg(q.numero, jsonb_array_length(q.alternativas) ORDER BY q.numero)
                      FROM questao_versao q WHERE q.versao_id = v.id) AS alternativas_por_questao
            FROM versao_avaliacao v JOIN avaliacao a ON a.id = v.avaliacao_id
            WHERE v.codigo = %s
            """,
            (codigo,),
        ).fetchone()
        if not linha:
            return None
        linha["gabarito"] = {int(n): l for n, l in linha["gabarito"].items()}
        linha["alternativas_por_questao"] = {int(n): q for n, q in linha["alternativas_por_questao"].items()}
        return VersaoPorCodigo(**linha)
