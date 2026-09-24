"""Avaliações, versões, QR Code e gabarito do aluno sobre o PostgreSQL (precisa de TEST_DATABASE_URL)."""

from dataclasses import replace

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.services.omr_service import _decodificar_qr
from app.services.qrcode_service import gerar_qrcode_png


def ler_qrcode(png: bytes) -> str:
    imagem = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_GRAYSCALE)
    lido = _decodificar_qr(imagem)
    return lido[0] if lido else ""


def criar_questoes(api, n=5) -> list[int]:
    ids = []
    for i in range(1, n + 1):
        resposta = api.post(
            "/api/questoes",
            json={"enunciado": f"Pergunta {i}", "alternativas": [f"q{i}a", f"q{i}b", f"q{i}c", f"q{i}d"],
                  "correta": "ABCD"[i % 4]},
        )
        ids.append(resposta.json()["id"])
    return ids


def criar_turma(api) -> int:
    semestre = api.post("/api/semestres", json={"nome": "2026/2"}).json()
    return api.post("/api/turmas", json={"semestre_id": semestre["id"], "nome": "ES-01"}).json()["id"]


def payload(questao_ids, **config):
    return {
        "nome": "N1 — Engenharia de Software",
        "questao_ids": questao_ids,
        "configuracao": {"quantidade": 3, "embaralhar_questoes": True, "embaralhar_alternativas": True, **config},
    }


@pytest.fixture
def questoes(api):
    return criar_questoes(api)


@pytest.fixture
def avaliacao(api, questoes):
    resposta = api.post("/api/avaliacoes", json={**payload(questoes), "turma_id": criar_turma(api)})
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


# --- Criação e persistência (RF14 a RF25) ------------------------------------------


def test_cria_avaliacao_com_versoes_e_gabaritos(avaliacao):
    assert [v["nome"] for v in avaliacao["versoes"]] == ["A", "B", "C"]
    assert avaliacao["gabarito_liberado"] is False
    assert avaliacao["turma_nome"] == "ES-01" and avaliacao["semestre_nome"] == "2026/2"
    assert avaliacao["nota_maxima"] == 10
    assert avaliacao["configuracao"]["embaralhar_alternativas"] is True
    for versao in avaliacao["versoes"]:
        assert len(versao["questoes"]) == 5
        assert versao["gabarito"] == {str(q["numero"]): q["correta"] for q in versao["questoes"]}


def test_gabarito_gravado_aponta_para_a_resposta_certa(api, questoes, avaliacao):
    corretas = {}
    for qid in questoes:
        q = api.get(f"/api/questoes/{qid}").json()
        corretas[str(qid)] = q["alternativas"]["ABCD".index(q["correta"])]

    for versao in avaliacao["versoes"]:
        for q in versao["questoes"]:
            assert q["alternativas"]["ABCD".index(q["correta"])] == corretas[q["questao_id"]]


def test_leitura_do_banco_igual_a_resposta_da_criacao(api, avaliacao):
    assert api.get(f"/api/avaliacoes/{avaliacao['id']}").json() == avaliacao


def test_grava_tudo_nas_tabelas(avaliacao, banco):
    def contar(tabela):
        return banco.execute(f"SELECT count(*) AS n FROM {tabela}").fetchone()["n"]

    assert contar("avaliacao") == 1
    assert contar("avaliacao_questao") == 5
    assert contar("versao_avaliacao") == 3
    assert contar("questao_versao") == 15
    assert contar("gabarito_versao") == 15


def test_falha_no_meio_nao_grava_nada(api, questoes, banco, monkeypatch):
    """N2-BE-04: se qualquer passo falhar, nada da avaliação fica no banco."""
    original = AvaliacaoRepository.criar

    def criar_e_falhar(self, *args, **kwargs):
        original(self, *args, **kwargs)
        raise RuntimeError("falha simulada depois de inserir tudo")

    monkeypatch.setattr(AvaliacaoRepository, "criar", criar_e_falhar)
    with pytest.raises(RuntimeError):
        api.post("/api/avaliacoes", json=payload(questoes))

    for tabela in ("avaliacao", "avaliacao_questao", "versao_avaliacao", "questao_versao", "gabarito_versao"):
        assert banco.execute(f"SELECT count(*) AS n FROM {tabela}").fetchone()["n"] == 0


def test_ordem_das_questoes_escolhida_pelo_professor(api, questoes):
    ordem = list(reversed(questoes))
    corpo = payload(ordem, quantidade=1, embaralhar_questoes=False, embaralhar_alternativas=False)
    versao = api.post("/api/avaliacoes", json=corpo).json()["versoes"][0]
    assert [int(q["questao_id"]) for q in versao["questoes"]] == ordem


def test_ajuste_do_gabarito_so_nesta_avaliacao(api, questoes):
    """RF16: o gabarito ajustado vale para a avaliação, sem mudar a questão no banco."""
    corpo = {**payload(questoes[:1], quantidade=1, embaralhar_alternativas=False), "gabaritos": {str(questoes[0]): "d"}}
    avaliacao = api.post("/api/avaliacoes", json=corpo).json()

    assert avaliacao["versoes"][0]["gabarito"] == {"1": "D"}
    assert api.get(f"/api/questoes/{questoes[0]}").json()["correta"] == "B"


@pytest.mark.parametrize(
    ("mudanca", "status", "trecho"),
    [
        ({"questao_ids": [999]}, 404, "não encontradas"),
        ({"turma_id": 999}, 404, "Turma"),
        ({"gabaritos": {"999": "A"}}, 422, "não foi selecionada"),
        ({"configuracao": {"quantidade": 3, "nomenclatura": "personalizada", "nomes_personalizados": ["X"]}}, 422,
         "exatamente 3"),
    ],
)
def test_entradas_invalidas(api, questoes, mudanca, status, trecho):
    resposta = api.post("/api/avaliacoes", json={**payload(questoes), **mudanca})
    assert resposta.status_code == status
    assert trecho in resposta.json()["detail"]


def test_questao_repetida_na_selecao(api, questoes):
    resposta = api.post("/api/avaliacoes", json=payload([questoes[0], questoes[0]]))
    assert resposta.status_code == 422


def test_editar_questao_nao_altera_prova_gerada(api, questoes, avaliacao):
    """RN14: a versão guarda uma cópia da questão."""
    antes = api.get(f"/api/avaliacoes/{avaliacao['id']}").json()
    api.put(f"/api/questoes/{questoes[0]}", json={"enunciado": "MUDOU", "alternativas": ["1", "2", "3", "4"],
                                                  "correta": "A"})
    assert api.get(f"/api/avaliacoes/{avaliacao['id']}").json() == antes


def test_excluir_questao_usada_mantem_a_prova(api, questoes, avaliacao):
    assert api.delete(f"/api/questoes/{questoes[0]}").json()["arquivada"] is True
    assert api.get(f"/api/avaliacoes/{avaliacao['id']}").json()["versoes"] == avaliacao["versoes"]


def test_listagem_resumida(api, avaliacao):
    resumo = api.get("/api/avaliacoes").json()
    assert len(resumo) == 1
    assert resumo[0]["quantidade_versoes"] == 3 and resumo[0]["quantidade_questoes"] == 5
    assert api.get("/api/avaliacoes", params={"turma_id": avaliacao["turma_id"]}).json() == resumo


def test_excluir_avaliacao_sem_correcoes(api, avaliacao, banco):
    assert api.delete(f"/api/avaliacoes/{avaliacao['id']}").status_code == 204
    assert banco.execute("SELECT count(*) AS n FROM versao_avaliacao").fetchone()["n"] == 0


def test_rotas_exigem_login(banco, banco_url, settings):
    with TestClient(create_app(replace(settings, database_url=banco_url))) as cliente:
        assert cliente.post("/api/avaliacoes", json={}).status_code == 401
        assert cliente.get("/api/avaliacoes").status_code == 401
        assert cliente.patch("/api/avaliacoes/1/gabarito", json={"liberado": True}).status_code == 401
        assert cliente.get("/api/avaliacoes/1/versoes/x/qrcode.png").status_code == 401


# --- QR Code (RF28) -----------------------------------------------------------------


def test_qrcode_png_codifica_o_conteudo():
    url = "https://exemplo.com/student/gabarito/abc"
    assert ler_qrcode(gerar_qrcode_png(url)) == url


def test_cada_versao_tem_codigo_proprio(avaliacao):
    codigos = [v["codigo"] for v in avaliacao["versoes"]]
    assert len(set(codigos)) == 3
    assert all(len(c) >= 12 for c in codigos)


def test_qrcode_da_versao_aponta_para_o_gabarito_do_aluno(api, avaliacao):
    versao = avaliacao["versoes"][1]
    resposta = api.get(versao["url_qrcode"])

    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "image/png"
    assert ler_qrcode(resposta.content) == versao["url_aluno"]
    assert versao["url_aluno"].endswith(f"/student/gabarito/{versao['codigo']}")


def test_qrcode_usa_url_publica_configurada(banco, banco_url, settings, questoes):
    config = replace(settings, database_url=banco_url, public_base_url="https://provafacil.exemplo.com/")
    with TestClient(create_app(config)) as cliente:
        cliente.post("/api/auth/login", json={"username": "professor", "password": "senha-teste"})
        versao = cliente.post("/api/avaliacoes", json=payload(questoes)).json()["versoes"][0]

        assert versao["url_aluno"] == f"https://provafacil.exemplo.com/student/gabarito/{versao['codigo']}"
        assert ler_qrcode(cliente.get(versao["url_qrcode"]).content) == versao["url_aluno"]


def test_qrcode_de_versao_de_outra_avaliacao_nao_existe(api, questoes, avaliacao):
    outra = api.post("/api/avaliacoes", json=payload(questoes)).json()
    url = f"/api/avaliacoes/{avaliacao['id']}/versoes/{outra['versoes'][0]['codigo']}/qrcode.png"
    assert api.get(url).status_code == 404


# --- Consulta do aluno (RF29, RF30, RN03 a RN05) ------------------------------------


def liberar(api, avaliacao, liberado=True):
    resposta = api.patch(f"/api/avaliacoes/{avaliacao['id']}/gabarito", json={"liberado": liberado})
    assert resposta.status_code == 200
    assert resposta.json()["gabarito_liberado"] is liberado


def test_aluno_ve_so_as_alternativas_corretas_da_sua_versao(api, avaliacao):
    liberar(api, avaliacao)
    api.post("/api/auth/logout")  # o aluno não tem login

    for versao in avaliacao["versoes"]:
        resposta = api.get(f"/student/gabarito/{versao['codigo']}")
        assert resposta.status_code == 200
        assert resposta.json() == {
            "avaliacao": "N1 — Engenharia de Software",
            "versao": versao["nome"],
            "gabarito": [{"questao": int(n), "alternativa": l} for n, l in versao["gabarito"].items()],
        }


def test_resposta_do_aluno_nao_expoe_dados_sensiveis(api, avaliacao):
    liberar(api, avaliacao)
    texto = api.get(f"/student/gabarito/{avaliacao['versoes'][0]['codigo']}").text
    for proibido in ("Pergunta", "enunciado", "nota", "turma", "semestre", "questao_id", "ordem_original"):
        assert proibido not in texto


def test_gabarito_bloqueado_ate_o_professor_liberar(api, avaliacao):
    url = f"/student/gabarito/{avaliacao['versoes'][0]['codigo']}"

    assert api.get(url).status_code == 403
    liberar(api, avaliacao)
    assert api.get(url).status_code == 200
    liberar(api, avaliacao, liberado=False)
    assert api.get(url).status_code == 403


def test_codigo_inexistente(api):
    resposta = api.get("/student/gabarito/nao-existe")
    assert resposta.status_code == 404
    assert "QR Code" in resposta.json()["detail"]
