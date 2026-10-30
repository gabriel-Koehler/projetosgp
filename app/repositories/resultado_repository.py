"""Consultas SQL dos resultados de correção (RF39, RF41 a RF48)."""

import psycopg
from psycopg.types.json import Jsonb

from app.models.resultado import QuestaoDaVersao, Resultado
from app.services.nota import ResultadoNota

SELECT = """
    SELECT r.id, r.avaliacao_id, a.nome AS avaliacao_nome, r.versao_id, v.nome AS versao_nome,
           r.aluno_id, al.nome AS aluno_nome, al.matricula, t.nome AS turma_nome, s.nome AS semestre_nome,
           r.respostas, r.gabarito, r.acertos, r.erros, r.em_branco, r.anuladas,
           r.nota::float AS nota, r.nota_maxima::float AS nota_maxima, r.origem, r.imagem_path, r.corrigido_em
    FROM resultado_correcao r
    JOIN avaliacao a ON a.id = r.avaliacao_id
    JOIN versao_avaliacao v ON v.id = r.versao_id
    LEFT JOIN aluno al ON al.id = r.aluno_id
    LEFT JOIN turma t ON t.id = COALESCE(al.turma_id, a.turma_id)
    LEFT JOIN semestre s ON s.id = t.semestre_id
"""


def _resultado(linha: dict) -> Resultado:
    linha["respostas"] = {int(n): r for n, r in linha["respostas"].items()}
    linha["gabarito"] = {int(n): g for n, g in linha["gabarito"].items()}
    return Resultado(**linha)


class ResultadoRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def salvar(
        self,
        avaliacao_id: int,
        versao_id: int,
        aluno_id: int | None,
        respostas: dict[int, str | None],
        gabarito: dict[int, str],
        nota: ResultadoNota,
        origem: str,
        imagem_path: str | None,
    ) -> int:
        """Grava o resultado. O mesmo aluno corrigido de novo na avaliação substitui o anterior."""
        return self.conn.execute(
            """
            INSERT INTO resultado_correcao (avaliacao_id, versao_id, aluno_id, respostas, gabarito, acertos, erros,
                                            em_branco, anuladas, nota, nota_maxima, origem, imagem_path)
            VALUES (%(avaliacao)s, %(versao)s, %(aluno)s, %(respostas)s, %(gabarito)s, %(acertos)s, %(erros)s,
                    %(em_branco)s, %(anuladas)s, %(nota)s, %(nota_maxima)s, %(origem)s, %(imagem)s)
            ON CONFLICT (avaliacao_id, aluno_id) WHERE aluno_id IS NOT NULL DO UPDATE SET
                versao_id = EXCLUDED.versao_id, respostas = EXCLUDED.respostas, gabarito = EXCLUDED.gabarito,
                acertos = EXCLUDED.acertos, erros = EXCLUDED.erros, em_branco = EXCLUDED.em_branco,
                anuladas = EXCLUDED.anuladas, nota = EXCLUDED.nota, nota_maxima = EXCLUDED.nota_maxima,
                origem = EXCLUDED.origem, imagem_path = EXCLUDED.imagem_path, corrigido_em = now()
            RETURNING id
            """,
            {
                "avaliacao": avaliacao_id,
                "versao": versao_id,
                "aluno": aluno_id,
                "respostas": Jsonb({str(n): r for n, r in respostas.items()}),
                "gabarito": Jsonb({str(n): g for n, g in gabarito.items()}),
                "acertos": nota.acertos,
                "erros": nota.erros,
                "em_branco": nota.em_branco,
                "anuladas": nota.anuladas,
                "nota": nota.nota,
                "nota_maxima": nota.nota_maxima,
                "origem": origem,
                "imagem": imagem_path,
            },
        ).fetchone()["id"]

    def obter(self, professor_id: int, resultado_id: int) -> Resultado | None:
        linha = self.conn.execute(SELECT + " WHERE a.professor_id = %s AND r.id = %s", (professor_id, resultado_id))
        linha = linha.fetchone()
        return _resultado(linha) if linha else None

    def listar(self, avaliacao_id: int) -> list[Resultado]:
        linhas = self.conn.execute(
            SELECT + " WHERE r.avaliacao_id = %s ORDER BY al.nome NULLS LAST, r.corrigido_em", (avaliacao_id,)
        ).fetchall()
        return [_resultado(l) for l in linhas]

    def excluir(self, resultado_id: int) -> None:
        self.conn.execute("DELETE FROM resultado_correcao WHERE id = %s", (resultado_id,))

    def questoes_das_versoes(self, avaliacao_id: int) -> list[QuestaoDaVersao]:
        linhas = self.conn.execute(
            """
            SELECT q.versao_id, q.numero, q.questao_id, q.enunciado, q.ordem_original
            FROM questao_versao q JOIN versao_avaliacao v ON v.id = q.versao_id
            WHERE v.avaliacao_id = %s
            """,
            (avaliacao_id,),
        ).fetchall()
        return [QuestaoDaVersao(**l) for l in linhas]

    def gabarito_original(self, avaliacao_id: int) -> list[dict]:
        """Questões selecionadas, na ordem da avaliação, com a letra correta no banco."""
        return self.conn.execute(
            """
            SELECT questao_id, ordem, correta FROM avaliacao_questao
            WHERE avaliacao_id = %s ORDER BY ordem
            """,
            (avaliacao_id,),
        ).fetchall()
