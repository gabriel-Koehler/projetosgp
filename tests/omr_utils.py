"""Gera "fotos" sintéticas de folhas preenchidas para testar a leitura OMR."""

import cv2
import numpy as np

from app.services import folha_layout as L
from app.services.folha_resposta import gerar_folha


def folha_preenchida(
    url: str,
    alternativas: list[int],
    marcas: dict[int, str | list[str]],
    intensidade: dict[int, float] | None = None,
) -> np.ndarray:
    """Folha canônica com as bolinhas pintadas. intensidade: questão -> tom (0 = preto, 200 = marca fraca)."""
    folha = np.array(gerar_folha("Prova de teste", "A", url, alternativas))
    return pintar(folha, alternativas, marcas, intensidade)


def pintar(folha: np.ndarray, alternativas: list[int], marcas: dict, intensidade: dict | None = None) -> np.ndarray:
    """Pinta as bolinhas de uma folha canônica (como o aluno faria com caneta)."""
    folha = folha.copy()
    layout = L.calcular_layout(len(alternativas), max(alternativas))
    for numero, letras in marcas.items():
        for letra in [letras] if isinstance(letras, str) else letras:
            cx, cy = layout.bolhas[numero]["ABCDE".index(letra)]
            tom = (intensidade or {}).get(numero, 30)
            cv2.circle(folha, (cx, cy), L.RAIO_BOLHA - 3, int(tom), -1)
    return folha


def fotografar(folha: np.ndarray, seed: int = 0, angulo: float = 4, perspectiva: float = 0.04,
               escala: float = 0.8, ruido: float = 8, sombra: bool = True) -> np.ndarray:
    """Coloca a folha sobre um fundo, com rotação, perspectiva, desfoque, ruído e sombra."""
    rng = np.random.default_rng(seed)
    h, w = folha.shape
    fundo_h, fundo_w = int(h * escala * 1.25), int(w * escala * 1.35)
    origem = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    centro = np.array([fundo_w / 2, fundo_h / 2])
    rad = np.deg2rad(angulo)
    rot = np.array([[np.cos(rad), -np.sin(rad)], [np.sin(rad), np.cos(rad)]])
    cantos = (origem - [w / 2, h / 2]) * escala @ rot.T + centro
    cantos += rng.uniform(-perspectiva, perspectiva, cantos.shape) * [w * escala, h * escala]
    matriz = cv2.getPerspectiveTransform(origem, cantos.astype(np.float32))
    foto = cv2.warpPerspective(folha, matriz, (fundo_w, fundo_h), borderValue=110)

    foto = cv2.GaussianBlur(foto, (3, 3), 0).astype(np.float32)
    if sombra:
        gradiente = np.linspace(0.65, 1.0, fundo_w)[None, :]
        foto *= gradiente
    foto += rng.normal(0, ruido, foto.shape)
    return np.clip(foto, 0, 255).astype(np.uint8)


def jpg(imagem: np.ndarray, qualidade: int = 85) -> bytes:
    return cv2.imencode(".jpg", imagem, [cv2.IMWRITE_JPEG_QUALITY, qualidade])[1].tobytes()
