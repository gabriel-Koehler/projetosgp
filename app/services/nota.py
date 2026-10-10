"""Cálculo da nota (RF37, RF38).

Regra: todas as questões valem o mesmo. nota = acertos / total de questões x nota máxima.
Em branco e mais de uma marcação (anulada) não pontuam.
"""

from dataclasses import dataclass

ANULADA = "*"  # valor gravado nas respostas quando o aluno marcou mais de uma alternativa


@dataclass(frozen=True)
class ResultadoNota:
    acertos: int
    erros: int  # marcou uma alternativa errada ou mais de uma (anulada)
    em_branco: int
    anuladas: int
    nota: float
    nota_maxima: float


def calcular_nota(respostas: dict[int, str | None], gabarito: dict[int, str], nota_maxima: float) -> ResultadoNota:
    if set(respostas) != set(gabarito):
        raise ValueError("As respostas não correspondem às questões da versão.")
    acertos = sum(1 for n, correta in gabarito.items() if respostas[n] == correta)
    em_branco = sum(1 for r in respostas.values() if r is None)
    anuladas = sum(1 for r in respostas.values() if r == ANULADA)
    total = len(gabarito)
    return ResultadoNota(
        acertos=acertos,
        erros=total - acertos - em_branco,
        em_branco=em_branco,
        anuladas=anuladas,
        nota=round(acertos / total * nota_maxima, 2),
        nota_maxima=nota_maxima,
    )


def situacao(resposta: str | None, correta: str) -> str:
    if resposta is None:
        return "em_branco"
    if resposta == ANULADA:
        return "anulada"
    return "correta" if resposta == correta else "errada"
