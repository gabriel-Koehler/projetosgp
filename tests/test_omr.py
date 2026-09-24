"""Leitura OMR com fotos sintéticas (rotação, perspectiva, desfoque, ruído e sombra)."""

import cv2
import numpy as np
import pytest
from omr_utils import folha_preenchida, fotografar, jpg

from app.services import folha_layout as L
from app.services import omr_service as O
from app.services.folha_resposta import folha_pdf, folha_png

URL = "https://provafacil.exemplo.com/student/gabarito/AbCdEfGh1234"
CODIGO = "AbCdEfGh1234"


def gabarito_ciclico(n, letras="ABCD"):
    return {i: letras[i % len(letras)] for i in range(1, n + 1)}


def ler(imagem: np.ndarray, alternativas: list[int]):
    return O.ler_folha(jpg(imagem), lambda codigo: dict(enumerate(alternativas, start=1)))


# --- Leitura correta ----------------------------------------------------------------


@pytest.mark.parametrize("seed", range(8))
def test_le_todas_as_respostas_em_fotos_diferentes(seed):
    marcas = gabarito_ciclico(30)
    foto = fotografar(folha_preenchida(URL, [4] * 30, marcas), seed=seed, angulo=(seed % 5 - 2) * 4)
    leitura = ler(foto, [4] * 30)

    assert leitura.codigo == CODIGO
    assert leitura.confiavel
    assert leitura.respostas == marcas


def test_folha_escaneada_sem_distorcao():
    marcas = gabarito_ciclico(10)
    folha = folha_preenchida(URL, [4] * 10, marcas)
    assert ler(folha, [4] * 10).respostas == marcas


def test_cinco_alternativas_e_tres_colunas():
    n = L.MAX_QUESTOES
    marcas = gabarito_ciclico(n, "ABCDE")
    foto = fotografar(folha_preenchida(URL, [5] * n, marcas), seed=3, escala=0.9)
    assert ler(foto, [5] * n).respostas == marcas


def test_questoes_com_quantidades_diferentes_de_alternativas():
    alternativas = [4, 5, 4, 5]
    marcas = {1: "D", 2: "E", 3: "A", 4: "E"}
    assert ler(fotografar(folha_preenchida(URL, alternativas, marcas)), alternativas).respostas == marcas


def test_sombra_forte():
    marcas = gabarito_ciclico(15)
    foto = fotografar(folha_preenchida(URL, [4] * 15, marcas), seed=5).astype(np.float32)
    foto *= np.linspace(0.45, 1.0, foto.shape[0])[:, None]
    assert ler(foto.astype(np.uint8), [4] * 15).respostas == marcas


@pytest.mark.parametrize("rotacao", [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE])
def test_foto_deitada_ou_de_cabeca_para_baixo(rotacao):
    marcas = gabarito_ciclico(12)
    foto = cv2.rotate(fotografar(folha_preenchida(URL, [4] * 12, marcas), seed=2, angulo=2), rotacao)
    leitura = ler(foto, [4] * 12)
    assert leitura.codigo == CODIGO
    assert leitura.respostas == marcas


# --- Situações de cada questão (RF35, RF36) -----------------------------------------


def test_em_branco_multipla_e_marca_fraca():
    marcas = gabarito_ciclico(10)
    del marcas[2]  # em branco
    marcas[5] = ["A", "C"]  # duas marcadas
    foto = fotografar(folha_preenchida(URL, [4] * 10, marcas, intensidade={8: 200}), seed=4)  # 8: marca fraca
    leitura = ler(foto, [4] * 10)
    situacoes = {q.numero: q.situacao for q in leitura.questoes}

    assert situacoes[2] == O.Situacao.EM_BRANCO
    assert situacoes[5] == O.Situacao.MULTIPLA
    assert situacoes[8] == O.Situacao.ILEGIVEL
    assert leitura.respostas[2] is None and leitura.respostas[5] is None and leitura.respostas[8] is None
    assert leitura.respostas[1] == "B"
    assert not leitura.confiavel  # RN15: marca duvidosa não gera resultado automático
    assert leitura.numeros(O.Situacao.ILEGIVEL) == [8]


def test_em_branco_e_multipla_nao_tornam_a_leitura_duvidosa():
    marcas = {1: "A", 3: ["B", "D"]}
    leitura = ler(fotografar(folha_preenchida(URL, [4] * 3, marcas)), [4] * 3)
    assert leitura.confiavel


@pytest.mark.parametrize(
    ("preenchimento", "situacao", "resposta"),
    [
        ([0.0, 0.9, 0.05, 0.0], O.Situacao.RESPONDIDA, "B"),
        ([0.0, 0.0, 0.0, 0.0], O.Situacao.EM_BRANCO, None),
        ([0.9, 0.0, 0.8, 0.0], O.Situacao.MULTIPLA, None),
        ([0.9, 0.3, 0.0, 0.0], O.Situacao.ILEGIVEL, None),  # rasura ao lado da marcada
        ([0.0, 0.0, 0.35, 0.0], O.Situacao.ILEGIVEL, None),  # marca fraca
    ],
)
def test_classificacao(preenchimento, situacao, resposta):
    questao = O.classificar(1, preenchimento)
    assert (questao.situacao, questao.resposta) == (situacao, resposta)


# --- Folhas que não dá para ler (RF36, RF40) ----------------------------------------


def test_canto_cortado():
    folha = folha_preenchida(URL, [4] * 10, gabarito_ciclico(10))
    cortada = folha[:, : L.LARGURA - 200]  # sem os marcadores da direita
    with pytest.raises(O.ErroLeitura) as erro:
        ler(fotografar(cortada), [4] * 10)
    assert erro.value.codigo == "folha_fora_do_padrao"


def test_qrcode_tapado():
    folha = folha_preenchida(URL, [4] * 10, gabarito_ciclico(10))
    folha[L.QR_Y : L.QR_Y + L.QR_LADO, L.QR_X : L.QR_X + L.QR_LADO] = 255
    with pytest.raises(O.ErroLeitura) as erro:
        ler(fotografar(folha), [4] * 10)
    assert erro.value.codigo == "qrcode_nao_lido"


@pytest.mark.parametrize("conteudo", [b"", b"nao e uma imagem"])
def test_arquivo_que_nao_e_imagem(conteudo):
    with pytest.raises(O.ErroLeitura) as erro:
        O.ler_folha(conteudo, lambda c: {})
    assert erro.value.codigo == "imagem_invalida"


def test_foto_sem_folha():
    papel_em_branco = np.full((1500, 1100), 200, np.uint8)
    with pytest.raises(O.ErroLeitura) as erro:
        ler(papel_em_branco, [4])
    assert erro.value.codigo == "folha_fora_do_padrao"


def test_erro_do_codigo_desconhecido_e_repassado():
    def desconhecido(codigo):
        raise O.ErroLeitura("prova_desconhecida", f"Código {codigo} não é de nenhuma prova.")

    folha = folha_preenchida(URL, [4] * 5, {})
    with pytest.raises(O.ErroLeitura) as erro:
        O.ler_folha(jpg(folha), desconhecido)
    assert erro.value.codigo == "prova_desconhecida"


# --- Folha impressa e layout (RF27) -------------------------------------------------


def test_codigo_extraido_da_url():
    assert O.extrair_codigo("https://x.com/student/gabarito/abc-123/") == "abc-123"
    assert O.extrair_codigo("abc-123") == "abc-123"


def test_folha_em_png_e_pdf():
    assert folha_png("Prova", "A", URL, [4] * 10).startswith(b"\x89PNG")
    assert folha_pdf("Prova", "A", URL, [4] * 10).startswith(b"%PDF")


def test_layout_cabe_na_folha_sem_sobrepor():
    layout = L.calcular_layout(L.MAX_QUESTOES, L.MAX_ALTERNATIVAS)
    centros = [c for bolhas in layout.bolhas.values() for c in bolhas]
    assert len(set(centros)) == len(centros)
    for x, y in centros:
        assert L.GRADE_ESQUERDA <= x - L.RAIO_BOLHA and x + L.RAIO_BOLHA <= L.GRADE_DIREITA
        assert L.GRADE_TOPO <= y - L.RAIO_BOLHA and y + L.RAIO_BOLHA <= L.GRADE_BASE


@pytest.mark.parametrize(("questoes", "alternativas"), [(0, 4), (L.MAX_QUESTOES + 1, 4), (10, 6), (10, 1)])
def test_layout_fora_dos_limites(questoes, alternativas):
    with pytest.raises(ValueError):
        L.calcular_layout(questoes, alternativas)
