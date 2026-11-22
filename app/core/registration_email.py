"""Envio do código de confirmação do cadastro de professor."""

import httpx

from app.core.config import Settings


def enviar_codigo(settings: Settings, email: str, codigo: str) -> None:
    httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": settings.registration_email_from,
            "to": [email],
            "subject": "Confirme seu e-mail no AvaliaSystem",
            "text": (
                f"Seu código de confirmação é {codigo}. "
                "Digite-o na tela de cadastro em até 15 minutos. "
                "Se você não solicitou o cadastro, ignore esta mensagem."
            ),
        },
        timeout=5,
    ).raise_for_status()
