"""Geometria da folha de respostas, compartilhada pela geração (impressão) e pela leitura (OMR).

Tudo em pixels da folha "canônica": A4 a 200 DPI (1654 x 2339). A foto da folha
é alinhada para esse tamanho pelos 4 marcadores pretos dos cantos, e então as
bolinhas ficam exatamente nas posições calculadas aqui.
"""

import math
from dataclasses import dataclass

LARGURA, ALTURA = 1654, 2339  # A4 a 200 DPI
DPI = 200

MARCADOR = 70  # lado do quadrado preto de cada canto
MARGEM = 50
CENTROS_MARCADORES = [  # superior esquerdo, superior direito, inferior direito, inferior esquerdo
    (MARGEM + MARCADOR / 2, MARGEM + MARCADOR / 2),
    (LARGURA - MARGEM - MARCADOR / 2, MARGEM + MARCADOR / 2),
    (LARGURA - MARGEM - MARCADOR / 2, ALTURA - MARGEM - MARCADOR / 2),
    (MARGEM + MARCADOR / 2, ALTURA - MARGEM - MARCADOR / 2),
]

QR_X, QR_Y, QR_LADO = 1190, 150, 300  # QR Code no alto, à direita

GRADE_TOPO = 640
GRADE_BASE = 2200
GRADE_ESQUERDA = 130
GRADE_DIREITA = LARGURA - 130
ALTURA_LINHA = 50
RAIO_BOLHA = 17
PASSO_BOLHA = 62  # distância entre os centros das bolinhas de uma questão
LARGURA_NUMERO = 80  # espaço do número da questão, à esquerda das bolinhas
LINHAS_POR_COLUNA = (GRADE_BASE - GRADE_TOPO) // ALTURA_LINHA  # 31
MAX_COLUNAS = 3
MAX_QUESTOES = LINHAS_POR_COLUNA * MAX_COLUNAS  # 93
MAX_ALTERNATIVAS = 5


@dataclass(frozen=True)
class Layout:
    colunas: int
    linhas_por_coluna: int
    # número da questão -> centros (x, y) das bolinhas A, B, C...
    bolhas: dict[int, list[tuple[int, int]]]
    # número da questão -> posição (x, y) do texto do número
    numeros: dict[int, tuple[int, int]]
    # x do início (número) de cada coluna
    inicio_colunas: list[int]


def calcular_layout(quantidade_questoes: int, alternativas: int) -> Layout:
    if not 1 <= quantidade_questoes <= MAX_QUESTOES:
        raise ValueError(f"A folha de respostas comporta de 1 a {MAX_QUESTOES} questões.")
    if not 2 <= alternativas <= MAX_ALTERNATIVAS:
        raise ValueError(f"A folha de respostas comporta de 2 a {MAX_ALTERNATIVAS} alternativas.")

    colunas = math.ceil(quantidade_questoes / LINHAS_POR_COLUNA)
    linhas = math.ceil(quantidade_questoes / colunas)
    largura_coluna = LARGURA_NUMERO + alternativas * PASSO_BOLHA
    espaco = (GRADE_DIREITA - GRADE_ESQUERDA - colunas * largura_coluna) / (colunas + 1)
    inicio_colunas = [round(GRADE_ESQUERDA + espaco + c * (largura_coluna + espaco)) for c in range(colunas)]

    bolhas, numeros = {}, {}
    for indice in range(quantidade_questoes):
        coluna, linha = divmod(indice, linhas)
        x0 = inicio_colunas[coluna]
        y = GRADE_TOPO + linha * ALTURA_LINHA + ALTURA_LINHA // 2
        numero = indice + 1
        numeros[numero] = (x0, y)
        bolhas[numero] = [
            (x0 + LARGURA_NUMERO + PASSO_BOLHA // 2 + a * PASSO_BOLHA, y) for a in range(alternativas)
        ]
    return Layout(colunas, linhas, bolhas, numeros, inicio_colunas)
