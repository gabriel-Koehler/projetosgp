"""Estatísticas da avaliação (RF44 a RF46).

As versões embaralham questões e alternativas, então tudo é convertido para a
questão e a letra ORIGINAIS do banco antes de contar: a "B" da versão A e a "D"
da versão B podem ser a mesma alternativa.
"""

import statistics
from collections import Counter
from dataclasses import dataclass, field

from app.models.resultado import QuestaoDaVersao, Resultado
from app.services.nota import ANULADA
from app.services.version_builder import indice_da_letra, letra


@dataclass
class EstatisticaQuestao:
    ordem: int  # posição na avaliação (ordem escolhida pelo professor)
    questao_id: int
    enunciado: str
    correta: str  # letra original
    respondentes: int
    acertos: int
    percentual_acerto: float
    escolhas: dict[str, int]  # letra original -> quantidade
    percentuais: dict[str, float]
    em_branco: int
    anuladas: int
    mais_escolhida: str | None  # RF45 (None se ninguém marcou)


@dataclass
class FaixaNota:
    de: float
    ate: float
    quantidade: int


@dataclass
class EstatisticaVersao:
    versao: str
    provas: int
    media: float | None


@dataclass
class Estatisticas:
    provas_corrigidas: int
    nota_maxima: float
    media: float | None = None
    mediana: float | None = None
    maior_nota: float | None = None
    menor_nota: float | None = None
    desvio_padrao: float | None = None
    media_acertos: float | None = None
    media_erros: float | None = None
    percentual_acerto: float | None = None
    distribuicao: list[FaixaNota] = field(default_factory=list)
    por_versao: list[EstatisticaVersao] = field(default_factory=list)
    por_questao: list[EstatisticaQuestao] = field(default_factory=list)


def _pct(parte: int, total: int) -> float:
    return round(100 * parte / total, 1) if total else 0.0


def distribuicao_notas(notas: list[float], nota_maxima: float, faixas: int = 10) -> list[FaixaNota]:
    passo = nota_maxima / faixas
    contagem = Counter(min(int(n / passo), faixas - 1) for n in notas)
    return [
        FaixaNota(de=round(i * passo, 2), ate=round((i + 1) * passo, 2), quantidade=contagem.get(i, 0))
        for i in range(faixas)
    ]


def calcular(
    resultados: list[Resultado],
    questoes_versoes: list[QuestaoDaVersao],
    selecionadas: list[dict],  # [{"questao_id", "ordem", "correta"}] da avaliação
    nota_maxima: float,
) -> Estatisticas:
    est = Estatisticas(provas_corrigidas=len(resultados), nota_maxima=nota_maxima)
    mapa = {(q.versao_id, q.numero): q for q in questoes_versoes}
    enunciados = {q.questao_id: q.enunciado for q in questoes_versoes}
    alternativas = {q.questao_id: len(q.ordem_original) for q in questoes_versoes}

    # Contagem por questão original.
    escolhas: dict[int, Counter] = {s["questao_id"]: Counter() for s in selecionadas}
    respondentes: Counter = Counter()
    for resultado in resultados:
        for numero, resposta in resultado.respostas.items():
            questao = mapa.get((resultado.versao_id, numero))
            if questao is None or questao.questao_id not in escolhas:
                continue
            respondentes[questao.questao_id] += 1
            if resposta is None:
                escolhas[questao.questao_id]["_branco"] += 1
            elif resposta == ANULADA:
                escolhas[questao.questao_id]["_anulada"] += 1
            else:
                original = questao.ordem_original[indice_da_letra(resposta)]
                escolhas[questao.questao_id][original] += 1

    for s in selecionadas:
        qid, contagem, total = s["questao_id"], escolhas[s["questao_id"]], respondentes[s["questao_id"]]
        letras = [letra(i) for i in range(alternativas.get(qid, 4))]
        por_letra = {l: contagem.get(l, 0) for l in letras}
        maximo = max(por_letra.values(), default=0)
        est.por_questao.append(
            EstatisticaQuestao(
                ordem=s["ordem"],
                questao_id=qid,
                enunciado=enunciados.get(qid, ""),
                correta=s["correta"],
                respondentes=total,
                acertos=por_letra.get(s["correta"], 0),
                percentual_acerto=_pct(por_letra.get(s["correta"], 0), total),
                escolhas=por_letra,
                percentuais={l: _pct(q, total) for l, q in por_letra.items()},
                em_branco=contagem.get("_branco", 0),
                anuladas=contagem.get("_anulada", 0),
                # Empate: a primeira letra entre as mais escolhidas.
                mais_escolhida=next((l for l, q in por_letra.items() if q == maximo), None) if maximo else None,
            )
        )

    if not resultados:
        return est

    notas = [r.nota for r in resultados]
    est.media = round(statistics.fmean(notas), 2)
    est.mediana = round(statistics.median(notas), 2)
    est.maior_nota, est.menor_nota = max(notas), min(notas)
    est.desvio_padrao = round(statistics.pstdev(notas), 2)
    est.media_acertos = round(statistics.fmean(r.acertos for r in resultados), 2)
    est.media_erros = round(statistics.fmean(r.erros for r in resultados), 2)
    total_questoes = sum(len(r.gabarito) for r in resultados)
    est.percentual_acerto = _pct(sum(r.acertos for r in resultados), total_questoes)
    est.distribuicao = distribuicao_notas(notas, nota_maxima)

    por_versao: dict[str, list[float]] = {}
    for r in resultados:
        por_versao.setdefault(r.versao_nome, []).append(r.nota)
    est.por_versao = [
        EstatisticaVersao(versao=v, provas=len(n), media=round(statistics.fmean(n), 2)) for v, n in por_versao.items()
    ]
    return est
