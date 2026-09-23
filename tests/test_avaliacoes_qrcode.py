import cv2
import numpy as np
import pytest

from app.services.qrcode_service import gerar_qrcode_png

QUESTOES = [
    {"id": f"Q{i}", "enunciado": f"Pergunta {i}", "alternativas": ["a", "b", "c", "d"], "correta": "ABCD"[i % 4]}
    for i in range(1, 6)
]


def payload(**config):
    return {
        "nome": "N1 — Engenharia de Software",
        "semestre": "2026/2",
        "turma": "ES-01",
        "questoes": QUESTOES,
        "configuracao": {"quantidade": 3, "embaralhar_questoes": True, "embaralhar_alternativas": True, **config},
    }


def ler_qrcode(png: bytes) -> str:
    imagem = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_GRAYSCALE)
    texto, _, _ = cv2.QRCodeDetector().detectAndDecode(imagem)
    return texto


@pytest.fixture
def avaliacao(client_logado):
    resposta = client_logado.post("/api/avaliacoes", json=payload())
    assert resposta.status_code == 201
    return resposta.json()


# --- Criação da avaliação e das versões (rotas do professor) ------------------


def test_cria_avaliacao_com_versoes_e_gabaritos(avaliacao):
    assert [v["nome"] for v in avaliacao["versoes"]] == ["A", "B", "C"]
    assert avaliacao["gabarito_liberado"] is False
    for versao in avaliacao["versoes"]:
        assert len(versao["questoes"]) == 5
        assert versao["gabarito"] == {str(q["numero"]): q["correta"] for q in versao["questoes"]}


def test_cada_versao_tem_codigo_proprio(avaliacao):
    codigos = [v["codigo"] for v in avaliacao["versoes"]]
    assert len(set(codigos)) == 3
    assert all(len(c) >= 12 for c in codigos)


def test_configuracao_invalida_retorna_mensagem_clara(client_logado):
    corpo = payload(nomenclatura="personalizada", nomes_personalizados=["Manhã"])
    resposta = client_logado.post("/api/avaliacoes", json=corpo)

    assert resposta.status_code == 422
    assert "exatamente 3 nome(s)" in resposta.json()["detail"]


def test_lista_e_obtem_avaliacao(client_logado, avaliacao):
    assert [a["id"] for a in client_logado.get("/api/avaliacoes").json()] == [avaliacao["id"]]
    assert client_logado.get(f"/api/avaliacoes/{avaliacao['id']}").json() == avaliacao
    assert client_logado.get("/api/avaliacoes/999").status_code == 404


def test_rotas_do_professor_exigem_login(client):
    assert client.post("/api/avaliacoes", json=payload()).status_code == 401
    assert client.get("/api/avaliacoes").status_code == 401
    assert client.patch("/api/avaliacoes/1/gabarito", json={"liberado": True}).status_code == 401
    assert client.get("/api/avaliacoes/1/versoes/x/qrcode.png").status_code == 401


# --- QR Code (RF28) ------------------------------------------------------------


def test_qrcode_png_codifica_o_conteudo():
    assert ler_qrcode(gerar_qrcode_png("https://exemplo.com/student/gabarito/abc")) == (
        "https://exemplo.com/student/gabarito/abc"
    )


def test_qrcode_da_versao_aponta_para_o_gabarito_do_aluno(client_logado, avaliacao):
    versao = avaliacao["versoes"][1]
    resposta = client_logado.get(versao["url_qrcode"])

    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "image/png"
    assert ler_qrcode(resposta.content) == versao["url_aluno"]
    assert versao["url_aluno"].endswith(f"/student/gabarito/{versao['codigo']}")


def test_qrcode_usa_url_publica_configurada(settings, client_logado, avaliacao):
    object.__setattr__(settings, "public_base_url", "https://provafacil.exemplo.com/")
    versao = client_logado.get(f"/api/avaliacoes/{avaliacao['id']}").json()["versoes"][0]

    assert versao["url_aluno"] == f"https://provafacil.exemplo.com/student/gabarito/{versao['codigo']}"
    assert ler_qrcode(client_logado.get(versao["url_qrcode"]).content) == versao["url_aluno"]


def test_qrcode_de_versao_de_outra_avaliacao_nao_existe(client_logado, avaliacao):
    outra = client_logado.post("/api/avaliacoes", json=payload()).json()
    codigo_da_outra = outra["versoes"][0]["codigo"]
    url = f"/api/avaliacoes/{avaliacao['id']}/versoes/{codigo_da_outra}/qrcode.png"
    assert client_logado.get(url).status_code == 404


# --- Consulta do aluno (RF29, RF30, RN03 a RN05) -------------------------------


def liberar(client, avaliacao, liberado=True):
    resposta = client.patch(f"/api/avaliacoes/{avaliacao['id']}/gabarito", json={"liberado": liberado})
    assert resposta.status_code == 200


def test_aluno_ve_so_as_alternativas_corretas_da_sua_versao(client_logado, avaliacao):
    liberar(client_logado, avaliacao)
    client_logado.post("/api/auth/logout")  # o aluno não tem login

    for versao in avaliacao["versoes"]:
        resposta = client_logado.get(f"/student/gabarito/{versao['codigo']}")
        assert resposta.status_code == 200
        assert resposta.json() == {
            "avaliacao": "N1 — Engenharia de Software",
            "versao": versao["nome"],
            "gabarito": [{"questao": int(n), "alternativa": l} for n, l in versao["gabarito"].items()],
        }


def test_resposta_do_aluno_nao_expoe_dados_sensiveis(client, client_logado, avaliacao):
    liberar(client_logado, avaliacao)
    texto = client.get(f"/student/gabarito/{avaliacao['versoes'][0]['codigo']}").text

    for proibido in ("Pergunta", "enunciado", "nota", "turma", "semestre", "questao_id", "ordem_original"):
        assert proibido not in texto


def test_gabarito_bloqueado_ate_o_professor_liberar(client_logado, avaliacao):
    url = f"/student/gabarito/{avaliacao['versoes'][0]['codigo']}"

    assert client_logado.get(url).status_code == 403
    liberar(client_logado, avaliacao)
    assert client_logado.get(url).status_code == 200
    liberar(client_logado, avaliacao, liberado=False)
    assert client_logado.get(url).status_code == 403


def test_codigo_inexistente(client):
    resposta = client.get("/student/gabarito/nao-existe")
    assert resposta.status_code == 404
    assert "QR Code" in resposta.json()["detail"]
