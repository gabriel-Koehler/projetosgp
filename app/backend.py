"""Compatibilidade N1: mesmas rotas da API persistente, com login local opcional."""
from app.core.config import Settings
from app.persistent import create_app as create_persistent_app


def create_app(settings: Settings | None = None):
    return create_persistent_app(settings, development_login=True)


app = create_app()
