from collections import Counter

import pytest

from app.services.version_builder import (
    ConfiguracaoVersoes,
    Nomenclatura,
    Questao,
    gerar_versoes,
    indice_da_letra,
    letra,
    nomes_das_versoes,
)


def banco(n: int = 10) -> list[Questao]:
    corretas = "ABCD"
    return [
        Questao(
            id=f"Q{i}",
            enunciado=f"Enunciado {i}",
            alternativas=[f"Q{i}-alt-{c}" for c in "ABCD"],
            correta=corretas[i % 4],
        )
        for i in range(1, n + 1)
    ]


def texto_correto_original(questao: Questao) -> str:
    return questao.alternativas[indice_da_letra(questao.correta)]


# --- RF25 / RN07: o embaralhamento preserva a resposta correta ---------------


@pytest.mark.parametrize("seed", range(50))
def test_gabarito_aponta_para_a_mesma_resposta_correta(seed):
    questoes = banco()
    por_id = {q.id: q for q in questoes}
    config = ConfiguracaoVersoes(quantidade=4, embaralhar_questoes=True, embaralhar_alternativas=True)

    for versao in gerar_versoes(questoes, config, seed=seed):
        for qv in versao.questoes:
            texto_no_gabarito = qv.alternativas[indice_da_letra(versao.gabarito[qv.numero])]
            assert texto_no_gabarito == texto_correto_original(por_id[qv.questao_id])


def test_alternativas_com_texto_repetido_nao_confundem_o_gabarito():
    # "Nenhuma" aparece duas vezes; só a posição D é a correta.
    questao = Questao("Q1", "Pergunta", ["Nenhuma", "Sim", "Não", "Nenhuma"], "D")
    config = ConfiguracaoVersoes(quantidade=20, embaralhar_alternativas=True)

    for versao in gerar_versoes([questao], config, seed=7):
        qv = versao.questoes[0]
        assert qv.ordem_original[indice_da_letra(qv.correta)] == "D"


def test_ordem_original_permite_voltar_para_a_letra_do_banco():
    questoes = banco(5)
    config = ConfiguracaoVersoes(quantidade=3, embaralhar_alternativas=True)

    for versao in gerar_versoes(questoes, config, seed=3):
        for qv, original in zip(versao.questoes, questoes):
            for pos, letra_original in enumerate(qv.ordem_original):
                assert qv.alternativas[pos] == original.alternativas[indice_da_letra(letra_original)]


# --- RF21 / RF22: embaralhamento SIM/NÃO -------------------------------------


def test_sem_embaralhar_mantem_ordem_do_banco():
    questoes = banco()
    versoes = gerar_versoes(questoes, ConfiguracaoVersoes(quantidade=3), seed=1)

    for versao in versoes:
        assert [q.questao_id for q in versao.questoes] == [q.id for q in questoes]
        for qv, original in zip(versao.questoes, questoes):
            assert qv.alternativas == original.alternativas
            assert qv.correta == original.correta


def test_embaralhar_questoes_altera_a_ordem_entre_versoes():
    config = ConfiguracaoVersoes(quantidade=4, embaralhar_questoes=True)
    ordens = {tuple(q.questao_id for q in v.questoes) for v in gerar_versoes(banco(), config, seed=42)}
    assert len(ordens) > 1


def test_embaralhar_so_alternativas_mantem_ordem_das_questoes():
    questoes = banco()
    config = ConfiguracaoVersoes(quantidade=3, embaralhar_alternativas=True)
    versoes = gerar_versoes(questoes, config, seed=42)

    for versao in versoes:
        assert [q.questao_id for q in versao.questoes] == [q.id for q in questoes]
    assert len({tuple(v.gabarito.values()) for v in versoes}) > 1


def test_numeracao_das_questoes_comeca_em_1():
    versao = gerar_versoes(banco(5), ConfiguracaoVersoes(quantidade=1, embaralhar_questoes=True), seed=0)[0]
    assert [q.numero for q in versao.questoes] == [1, 2, 3, 4, 5]
    assert list(versao.gabarito) == [1, 2, 3, 4, 5]


def test_mesma_seed_gera_mesmo_resultado():
    config = ConfiguracaoVersoes(quantidade=3, embaralhar_questoes=True, embaralhar_alternativas=True)
    assert gerar_versoes(banco(), config, seed=9) == gerar_versoes(banco(), config, seed=9)


def test_nao_altera_as_questoes_recebidas():
    questoes = banco()
    copia = [Questao(q.id, q.enunciado, list(q.alternativas), q.correta) for q in questoes]
    gerar_versoes(questoes, ConfiguracaoVersoes(quantidade=3, embaralhar_questoes=True, embaralhar_alternativas=True))
    assert questoes == copia


# --- RF19 / RF20: mesmas questões ou conjuntos diferentes ---------------------


def test_mesmas_questoes_em_todas_as_versoes():
    config = ConfiguracaoVersoes(quantidade=3, embaralhar_questoes=True)
    for versao in gerar_versoes(banco(), config, seed=5):
        assert sorted(q.questao_id for q in versao.questoes) == sorted(q.id for q in banco())


def test_conjuntos_diferentes_nao_se_repetem_quando_ha_questoes_suficientes():
    config = ConfiguracaoVersoes(quantidade=3, mesmas_questoes=False, questoes_por_versao=4)
    versoes = gerar_versoes(banco(12), config, seed=5)

    conjuntos = [{q.questao_id for q in v.questoes} for v in versoes]
    assert all(len(c) == 4 for c in conjuntos)
    assert set.union(*conjuntos) == {f"Q{i}" for i in range(1, 13)}
    assert sum(len(c) for c in conjuntos) == 12  # nenhuma questão em duas versões


def test_conjuntos_diferentes_com_poucas_questoes_distribuem_repeticoes():
    # 3 versões x 4 questões = 12 posições para 6 questões: cada uma aparece 2 vezes.
    config = ConfiguracaoVersoes(quantidade=3, mesmas_questoes=False, questoes_por_versao=4)
    versoes = gerar_versoes(banco(6), config, seed=5)

    for versao in versoes:
        ids = [q.questao_id for q in versao.questoes]
        assert len(ids) == len(set(ids)) == 4  # sem repetição dentro da mesma versão
    uso = Counter(q.questao_id for v in versoes for q in v.questoes)
    assert set(uso.values()) == {2}


def test_conjuntos_diferentes_sem_embaralhar_mantem_ordem_do_banco():
    questoes = banco(12)
    posicao = {q.id: i for i, q in enumerate(questoes)}
    config = ConfiguracaoVersoes(quantidade=3, mesmas_questoes=False, questoes_por_versao=4)

    for versao in gerar_versoes(questoes, config, seed=5):
        posicoes = [posicao[q.questao_id] for q in versao.questoes]
        assert posicoes == sorted(posicoes)


# --- RF17 / RF18 / RN08: quantidade e nomes das versões -----------------------


def test_quantidade_de_versoes_livre():
    assert len(gerar_versoes(banco(), ConfiguracaoVersoes(quantidade=30))) == 30


@pytest.mark.parametrize(
    ("nomenclatura", "esperado"),
    [
        (Nomenclatura.LETRAS, ["A", "B", "C"]),
        (Nomenclatura.NUMEROS, ["1", "2", "3"]),
        (Nomenclatura.CORES, ["Azul", "Verde", "Amarela"]),
    ],
)
def test_nomenclaturas(nomenclatura, esperado):
    assert nomes_das_versoes(ConfiguracaoVersoes(quantidade=3, nomenclatura=nomenclatura)) == esperado


def test_letras_passam_de_z_para_aa():
    assert [letra(i) for i in (0, 25, 26, 27, 51, 52)] == ["A", "Z", "AA", "AB", "AZ", "BA"]


def test_cores_repetem_com_sufixo_quando_acabam():
    nomes = nomes_das_versoes(ConfiguracaoVersoes(quantidade=12, nomenclatura=Nomenclatura.CORES))
    assert nomes[9:] == ["Marrom", "Azul 2", "Verde 2"]
    assert len(set(nomes)) == 12


def test_nomes_personalizados():
    config = ConfiguracaoVersoes(
        quantidade=2, nomenclatura=Nomenclatura.PERSONALIZADA, nomes_personalizados=["Manhã", "Noite"]
    )
    assert [v.nome for v in gerar_versoes(banco(), config)] == ["Manhã", "Noite"]


@pytest.mark.parametrize("nomes", [["A"], ["A", "B", "C"], ["A", " "], ["Manhã", "manhã"]])
def test_nomes_personalizados_invalidos(nomes):
    config = ConfiguracaoVersoes(quantidade=2, nomenclatura=Nomenclatura.PERSONALIZADA, nomes_personalizados=nomes)
    with pytest.raises(ValueError):
        nomes_das_versoes(config)


# --- Validações ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("questoes", "config"),
    [
        (banco(), ConfiguracaoVersoes(quantidade=0)),
        ([], ConfiguracaoVersoes(quantidade=1)),
        (banco(2) + banco(1), ConfiguracaoVersoes(quantidade=1)),  # questão duplicada
        ([Questao("Q1", "x", ["a", "b", "c", "d"], "E")], ConfiguracaoVersoes(quantidade=1)),
        ([Questao("Q1", "x", ["a", "b", "c", "d"], "?")], ConfiguracaoVersoes(quantidade=1)),
        ([Questao("Q1", "x", ["a"], "A")], ConfiguracaoVersoes(quantidade=1)),
        (banco(3), ConfiguracaoVersoes(quantidade=2, mesmas_questoes=False, questoes_por_versao=4)),
    ],
)
def test_entradas_invalidas(questoes, config):
    with pytest.raises(ValueError):
        gerar_versoes(questoes, config)


def test_gabarito_aceita_letra_minuscula():
    versao = gerar_versoes([Questao("Q1", "x", ["a", "b", "c", "d"], "c")], ConfiguracaoVersoes(quantidade=1))[0]
    assert versao.gabarito == {1: "C"}
