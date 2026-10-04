"""Geração do QR Code impresso na prova (RF28)."""

import io

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def gerar_qrcode_png(conteudo: str, tamanho_modulo: int = 10) -> bytes:
    # Correção de erro M (~15%) aguenta pequenas falhas de impressão e leitura na correção.
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=tamanho_modulo, border=4)
    qr.add_data(conteudo)
    qr.make(fit=True)
    imagem = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    return buffer.getvalue()
