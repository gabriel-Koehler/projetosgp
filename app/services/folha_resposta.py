"""Geração da folha de respostas para impressão (RF27), em PNG ou PDF (A4).

A folha é gerada no back-end para que o layout impresso seja exatamente o que
a leitura automática (omr_service) espera.
"""

import io
import unicodedata
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.services import folha_layout as L
from app.services.qrcode_service import gerar_qrcode_png
from app.services.version_builder import letra

FONTES = [
    "arial.ttf", "arialbd.ttf",  # Windows
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


@lru_cache
def _fonte(tamanho: int, negrito: bool = False) -> tuple[ImageFont.FreeTypeFont, bool]:
    """Devolve (fonte, tem_acentos)."""
    candidatas = [f for f in FONTES if ("bd" in f.lower() or "bold" in f.lower()) == negrito]
    for caminho in candidatas:
        try:
            if "/" not in caminho or Path(caminho).exists():
                return ImageFont.truetype(caminho, tamanho), True
        except OSError:
            continue
    return ImageFont.load_default(size=tamanho), False  # fonte embutida: sem acentos


def _texto(desenho: ImageDraw.ImageDraw, posicao, texto: str, tamanho: int, negrito=False, **kwargs) -> None:
    fonte, tem_acentos = _fonte(tamanho, negrito)
    if not tem_acentos:
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    desenho.text(posicao, texto, font=fonte, fill=0, **kwargs)


def gerar_folha(
    avaliacao: str, versao: str, url_qrcode: str, alternativas_por_questao: list[int]
) -> Image.Image:
    quantidade = len(alternativas_por_questao)
    layout = L.calcular_layout(quantidade, max(alternativas_por_questao))
    folha = Image.new("L", (L.LARGURA, L.ALTURA), 255)
    desenho = ImageDraw.Draw(folha)

    # Marcadores dos cantos: é por eles que a foto é alinhada.
    for cx, cy in L.CENTROS_MARCADORES:
        meio = L.MARCADOR / 2
        desenho.rectangle((cx - meio, cy - meio, cx + meio - 1, cy + meio - 1), fill=0)

    qr = Image.open(io.BytesIO(gerar_qrcode_png(url_qrcode, tamanho_modulo=8))).convert("L")
    folha.paste(qr.resize((L.QR_LADO, L.QR_LADO), Image.Resampling.NEAREST), (L.QR_X, L.QR_Y))

    _texto(desenho, (150, 160), "FOLHA DE RESPOSTAS", 44, negrito=True)
    _texto(desenho, (150, 230), avaliacao[:60], 32)
    _texto(desenho, (150, 280), f"Versão: {versao}", 32, negrito=True)
    _texto(desenho, (150, 360), "Nome: " + "_" * 44, 28)
    _texto(desenho, (150, 420), "Matrícula: " + "_" * 20, 28)
    _texto(desenho, (150, 500), "Preencha totalmente uma bolinha por questão, com caneta preta ou azul.", 24)
    _texto(desenho, (150, 535), "Não rasure, não dobre e não escreva perto dos quadrados pretos dos cantos.", 24)

    for inicio in layout.inicio_colunas:  # letras acima de cada coluna
        for a in range(max(alternativas_por_questao)):
            x = inicio + L.LARGURA_NUMERO + L.PASSO_BOLHA // 2 + a * L.PASSO_BOLHA
            _texto(desenho, (x, L.GRADE_TOPO - 30), letra(a), 26, negrito=True, anchor="mm")

    r = L.RAIO_BOLHA
    for numero, centros in layout.bolhas.items():
        x, y = layout.numeros[numero]
        _texto(desenho, (x + L.LARGURA_NUMERO - 18, y), f"{numero:02d}", 26, negrito=True, anchor="rm")
        for cx, cy in centros[: alternativas_por_questao[numero - 1]]:
            desenho.ellipse((cx - r, cy - r, cx + r, cy + r), outline=90, width=2)
    return folha


def folha_png(*args, **kwargs) -> bytes:
    saida = io.BytesIO()
    gerar_folha(*args, **kwargs).save(saida, format="PNG", dpi=(L.DPI, L.DPI))
    return saida.getvalue()


def folha_pdf(*args, **kwargs) -> bytes:
    saida = io.BytesIO()
    gerar_folha(*args, **kwargs).convert("RGB").save(saida, format="PDF", resolution=L.DPI)
    return saida.getvalue()
