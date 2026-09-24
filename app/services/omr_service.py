"""Leitura automática da folha de respostas por foto ou scan (RF32 a RF36, RF40, RN15).

Etapas:
1. Encontra os 4 marcadores pretos dos cantos e "desentorta" a foto para a folha canônica.
2. Lê o QR Code (pyzbar; se não houver, OpenCV) e extrai o código da versão.
3. Mede quanto de cada bolinha está preenchido e classifica cada questão.

Na dúvida, a leitura NÃO é confiável: o professor precisa ler de novo ou conferir (RN15).
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

import cv2
import numpy as np

from app.services import folha_layout as L
from app.services.version_builder import letra

try:  # pyzbar precisa da biblioteca do sistema libzbar (no Linux: apt install libzbar0)
    from pyzbar import pyzbar
except ImportError:  # pragma: no cover - depende do sistema
    pyzbar = None

# Escuridão média do miolo da bolinha: 0 = papel em branco, 1 = totalmente pintada.
# Em fotos de teste: vazias ficam abaixo de 0.12, pintadas acima de 0.85, marca fraca ~0.3.
MARCADA = 0.55  # a partir daqui a bolinha está preenchida
DUVIDOSA = 0.20  # entre DUVIDOSA e MARCADA: rasura, marca fraca ou "X" -> não confiável
RAIO_MEDIDO = 0.6  # mede só o miolo da bolinha, sem o contorno impresso
LADO_MAXIMO = 2500  # fotos maiores são reduzidas antes de processar


class Situacao(str, Enum):
    RESPONDIDA = "respondida"
    EM_BRANCO = "em_branco"
    MULTIPLA = "multipla"  # mais de uma alternativa marcada: questão anulada
    ILEGIVEL = "ilegivel"  # marca duvidosa: exige nova leitura ou conferência


class ErroLeitura(Exception):
    """Folha que não dá para ler: fora do padrão, sem QR Code ou de outra prova."""

    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem


@dataclass(frozen=True)
class LeituraQuestao:
    numero: int
    situacao: Situacao
    resposta: str | None
    preenchimento: list[float]  # fração preenchida de cada alternativa (A, B, C...)


@dataclass
class LeituraFolha:
    codigo: str
    questoes: list[LeituraQuestao] = field(default_factory=list)

    @property
    def respostas(self) -> dict[int, str | None]:
        return {q.numero: q.resposta for q in self.questoes}

    @property
    def confiavel(self) -> bool:
        return not any(q.situacao == Situacao.ILEGIVEL for q in self.questoes)

    def numeros(self, situacao: Situacao) -> list[int]:
        return [q.numero for q in self.questoes if q.situacao == situacao]


def carregar_imagem(conteudo: bytes) -> np.ndarray:
    imagem = cv2.imdecode(np.frombuffer(conteudo, np.uint8), cv2.IMREAD_GRAYSCALE) if conteudo else None
    if imagem is None:
        raise ErroLeitura("imagem_invalida", "Não foi possível abrir a imagem. Envie uma foto JPG ou PNG.")
    maior = max(imagem.shape)
    if maior > LADO_MAXIMO:
        escala = LADO_MAXIMO / maior
        imagem = cv2.resize(imagem, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    return imagem


def _quadrados_cheios(binaria: np.ndarray, area_minima: float) -> list[tuple[float, float, float]]:
    """(x, y, área) dos quadrados pretos cheios. RETR_LIST: o marcador fica "dentro" da folha,
    que por sua vez fica dentro do fundo da foto."""
    contornos, _ = cv2.findContours(binaria, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = []
    for contorno in contornos:
        area = cv2.contourArea(contorno)
        if area < area_minima:
            continue
        aproximado = cv2.approxPolyDP(contorno, 0.05 * cv2.arcLength(contorno, True), True)
        _, _, w, h = cv2.boundingRect(aproximado)
        if len(aproximado) != 4 or not 0.7 <= w / h <= 1.4:
            continue
        # Marcador é um quadrado cheio; o QR Code, a folha e os textos não são.
        if area / cv2.contourArea(cv2.convexHull(contorno)) < 0.9:
            continue
        (_, _), (lado_a, lado_b), _ = cv2.minAreaRect(contorno)
        if area / max(lado_a * lado_b, 1) < 0.85:
            continue
        # Pixels pretos dentro do contorno: o quadrado de canto do QR Code é "vazado" e cai aqui.
        x, y, w, h = cv2.boundingRect(contorno)
        mascara = np.zeros((h, w), np.uint8)
        cv2.drawContours(mascara, [contorno - [x, y]], -1, 255, -1)
        dentro = cv2.countNonZero(cv2.bitwise_and(binaria[y : y + h, x : x + w], mascara))
        if dentro / max(cv2.countNonZero(mascara), 1) < 0.85:
            continue
        momento = cv2.moments(contorno)
        candidatos.append((momento["m10"] / momento["m00"], momento["m01"] / momento["m00"], area))
    return candidatos


def _selecionar_cantos(candidatos: list[tuple[float, float, float]], largura: int, altura: int) -> np.ndarray | None:
    """O candidato mais perto de cada canto da foto, se os 4 formarem uma folha A4."""
    if len(candidatos) < 4:
        return None
    cantos = [(0, 0), (largura, 0), (largura, altura), (0, altura)]
    escolhidos = [min(candidatos, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2) for x, y in cantos]
    pontos = np.array([c[:2] for c in escolhidos], dtype=np.float32)
    areas = [c[2] for c in escolhidos]

    lados = [np.linalg.norm(pontos[i] - pontos[(i + 1) % 4]) for i in range(4)]
    esperado = (L.CENTROS_MARCADORES[3][1] - L.CENTROS_MARCADORES[0][1]) / (
        L.CENTROS_MARCADORES[1][0] - L.CENTROS_MARCADORES[0][0]
    )
    proporcao = (lados[1] + lados[3]) / (lados[0] + lados[2])
    if (
        len({tuple(p) for p in pontos}) != 4
        or not cv2.isContourConvex(pontos.reshape(-1, 1, 2))
        or not 0.75 * esperado <= proporcao <= 1.3 * esperado
        or max(areas) > 4 * min(areas)
    ):
        return None
    return pontos


def _encontrar_marcadores(cinza: np.ndarray) -> np.ndarray:
    """Centros dos 4 marcadores na ordem: sup. esquerdo, sup. direito, inf. direito, inf. esquerdo."""
    altura, largura = cinza.shape
    suave = cv2.GaussianBlur(cinza, (5, 5), 0)
    _, otsu = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    bloco = (min(altura, largura) // 8) | 1  # adaptativo: aguenta sombra forte
    adaptativa = cv2.adaptiveThreshold(suave, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, bloco, 25)

    for binaria in (otsu, adaptativa):
        pontos = _selecionar_cantos(_quadrados_cheios(binaria, altura * largura * 0.0003), largura, altura)
        if pontos is not None:
            return pontos
    raise ErroLeitura(
        "folha_fora_do_padrao",
        "Folha fora do padrão: não encontrei os 4 quadrados pretos dos cantos. "
        "Fotografe a folha inteira, de frente e sem cortar os cantos.",
    )


def alinhar_folha(cinza: np.ndarray) -> np.ndarray:
    try:
        origem = _encontrar_marcadores(cinza)
    except ErroLeitura:
        # Foto tirada "deitada": gira 90° e tenta de novo (os 180° são corrigidos pelo QR Code).
        cinza = cv2.rotate(cinza, cv2.ROTATE_90_CLOCKWISE)
        origem = _encontrar_marcadores(cinza)
    destino = np.array(L.CENTROS_MARCADORES, dtype=np.float32)
    matriz = cv2.getPerspectiveTransform(origem, destino)
    return cv2.warpPerspective(cinza, matriz, (L.LARGURA, L.ALTURA), flags=cv2.INTER_LINEAR, borderValue=255)


def _decodificar_qr(imagem: np.ndarray) -> tuple[str, tuple[float, float]] | None:
    """Texto do QR Code e o centro dele na imagem."""
    if pyzbar is not None:
        for resultado in pyzbar.decode(imagem, symbols=[pyzbar.ZBarSymbol.QRCODE]):
            r = resultado.rect
            return resultado.data.decode("utf-8", "replace"), (r.left + r.width / 2, r.top + r.height / 2)
    texto, pontos, _ = cv2.QRCodeDetector().detectAndDecode(imagem)
    if texto and pontos is not None:
        centro = pontos.reshape(-1, 2).mean(axis=0)
        return texto, (float(centro[0]), float(centro[1]))
    return None


def extrair_codigo(texto: str) -> str:
    """O QR Code contém a URL do gabarito do aluno; o código é o último trecho."""
    return texto.strip().rstrip("/").rsplit("/", 1)[-1]


def ler_qrcode(folha: np.ndarray) -> tuple[str, np.ndarray]:
    """Devolve o código e a folha na orientação certa (foto de cabeça para baixo é girada)."""
    for tentativa in (folha, cv2.rotate(folha, cv2.ROTATE_180)):
        regiao_qr = tentativa[: L.QR_Y + L.QR_LADO + 150, L.QR_X - 150 :]
        lido = _decodificar_qr(regiao_qr)
        if lido is not None:
            return extrair_codigo(lido[0]), tentativa
    raise ErroLeitura(
        "qrcode_nao_lido",
        "Não foi possível ler o QR Code da folha. Fotografe de novo, com boa luz e sem reflexo.",
    )


def normalizar(folha: np.ndarray) -> np.ndarray:
    """Escuridão de 0 (papel) a 1 (tinta), compensando sombras e iluminação desigual.

    O fundo (cor do papel em cada ponto) é estimado com uma dilatação, que apaga
    a tinta e as bolinhas, seguida de um desfoque.
    """
    fundo = cv2.dilate(folha, cv2.getStructuringElement(cv2.MORPH_RECT, (45, 45)))
    fundo = cv2.GaussianBlur(fundo, (0, 0), 15)
    normalizada = cv2.divide(folha, fundo, scale=255).astype(np.float32)
    return np.clip((255 - normalizada) / 255, 0, 1)


def _preenchimentos(escuridao: np.ndarray, centros: list[tuple[int, int]]) -> list[float]:
    raio = max(3, int(L.RAIO_BOLHA * RAIO_MEDIDO))
    mascara = np.zeros((2 * raio + 1, 2 * raio + 1), np.float32)
    cv2.circle(mascara, (raio, raio), raio, 1, -1)
    total = float(mascara.sum())
    valores = []
    for cx, cy in centros:
        recorte = escuridao[cy - raio : cy + raio + 1, cx - raio : cx + raio + 1]
        valores.append(round(float((recorte * mascara).sum()) / total, 3))
    return valores


def classificar(numero: int, preenchimento: list[float]) -> LeituraQuestao:
    marcadas = [i for i, v in enumerate(preenchimento) if v >= MARCADA]
    duvidosas = [i for i, v in enumerate(preenchimento) if DUVIDOSA <= v < MARCADA]
    if duvidosas:
        return LeituraQuestao(numero, Situacao.ILEGIVEL, None, preenchimento)
    if not marcadas:
        return LeituraQuestao(numero, Situacao.EM_BRANCO, None, preenchimento)
    if len(marcadas) > 1:
        return LeituraQuestao(numero, Situacao.MULTIPLA, None, preenchimento)
    return LeituraQuestao(numero, Situacao.RESPONDIDA, letra(marcadas[0]), preenchimento)


def ler_folha(conteudo: bytes, alternativas_da_versao: Callable[[str], dict[int, int]]) -> LeituraFolha:
    """Lê a folha. `alternativas_da_versao(codigo)` devolve {número da questão: quantidade de alternativas}
    da versão identificada pelo QR Code (ou lança ErroLeitura se o código não for de uma prova conhecida).
    """
    folha = alinhar_folha(carregar_imagem(conteudo))
    codigo, folha = ler_qrcode(folha)
    alternativas = alternativas_da_versao(codigo)

    layout = L.calcular_layout(len(alternativas), max(alternativas.values()))
    escuridao = normalizar(folha)
    leitura = LeituraFolha(codigo=codigo)
    for numero in sorted(alternativas):
        centros = layout.bolhas[numero][: alternativas[numero]]
        leitura.questoes.append(classificar(numero, _preenchimentos(escuridao, centros)))
    return leitura
