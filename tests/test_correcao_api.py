"""Leitura da folha pela API: folha baixada do sistema, "preenchida" e fotografada (precisa de TEST_DATABASE_URL)."""

import cv2
import numpy as np
import pytest
from omr_utils import fotografar, jpg, pintar

from app.services import folha_layout as L


@pytest.fixture
def avaliacao(api):
    ids = []
    for i in range(1, 9):
        alternativas = ["a", "b", "c", "d", "e"] if i == 8 else ["a", "b", "c", "d"]
        resposta = api.post("/api/questoes", json={"enunciado": f"Q{i}", "alternativas": alternativas, "correta": "A"})
        ids.append(resposta.json()["id"])
    corpo = {
        "nome": "N1 — Engenharia de Software",
        "questao_ids": ids,
        "configuracao": {"quantidade": 2, "embaralhar_questoes": True, "embaralhar_alternativas": True},
    }
    return api.post("/api/avaliacoes", json=corpo).json()


def baixar_folha(api, avaliacao, versao) -> np.ndarray:
    resposta = api.get(f"/api/avaliacoes/{avaliacao['id']}/versoes/{versao['codigo']}/folha.png")
    assert resposta.status_code == 200
    return cv2.imdecode(np.frombuffer(resposta.content, np.uint8), cv2.IMREAD_GRAYSCALE)


def enviar(api, imagem: np.ndarray):
    return api.post("/api/correcoes/leitura", files={"imagem": ("folha.jpg", jpg(imagem), "image/jpeg")})


def test_folha_para_impressao(api, avaliacao):
    versao = avaliacao["versoes"][0]
    pdf = api.get(f"/api/avaliacoes/{avaliacao['id']}/versoes/{versao['codigo']}/folha.pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
    assert baixar_folha(api, avaliacao, versao).shape == (L.ALTURA, L.LARGURA)


def test_le_a_folha_e_identifica_a_versao(api, avaliacao):
    versao = avaliacao["versoes"][1]
    alternativas = [len(q["alternativas"]) for q in versao["questoes"]]
    marcas = {int(n): letra for n, letra in versao["gabarito"].items()}  # aluno que acertou tudo
    del marcas[3]
    marcas[4] = ["A", "B"]

    foto = fotografar(pintar(baixar_folha(api, avaliacao, versao), alternativas, marcas), seed=7)
    resposta = enviar(api, foto)
    assert resposta.status_code == 200, resposta.text
    leitura = resposta.json()

    assert leitura["codigo"] == versao["codigo"]
    assert leitura["versao"] == versao["nome"]
    assert leitura["avaliacao_id"] == avaliacao["id"]
    assert leitura["confiavel"] is True
    assert leitura["em_branco"] == [3] and leitura["multiplas"] == [4] and leitura["ilegiveis"] == []
    esperado = {str(n): l for n, l in marcas.items() if n != 4} | {"3": None, "4": None}
    assert leitura["respostas"] == dict(sorted(esperado.items(), key=lambda kv: int(kv[0])))
    assert "em branco: 3" in leitura["mensagem"]


def test_marca_duvidosa_pede_nova_leitura(api, avaliacao):
    versao = avaliacao["versoes"][0]
    alternativas = [len(q["alternativas"]) for q in versao["questoes"]]
    folha = pintar(baixar_folha(api, avaliacao, versao), alternativas, {1: "A", 2: "B"}, intensidade={2: 200})
    leitura = enviar(api, fotografar(folha)).json()

    assert leitura["confiavel"] is False
    assert leitura["ilegiveis"] == [2]
    assert "Fotografe de novo" in leitura["mensagem"]


def test_folha_fora_do_padrao(api):
    resposta = enviar(api, np.full((1200, 900), 230, np.uint8))
    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "folha_fora_do_padrao"


def test_folha_de_outro_professor_ou_inexistente(api, avaliacao):
    versao = avaliacao["versoes"][0]
    folha = baixar_folha(api, avaliacao, versao)
    api.delete(f"/api/avaliacoes/{avaliacao['id']}")  # a prova deixa de existir
    resposta = enviar(api, folha)
    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "prova_desconhecida"


def test_arquivo_invalido(api):
    resposta = api.post("/api/correcoes/leitura", files={"imagem": ("x.txt", b"texto", "text/plain")})
    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "imagem_invalida"
