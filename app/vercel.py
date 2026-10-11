"""Entrada ASGI da Vercel, sem estado mock ou login de demonstração."""
from app.persistent import create_app

app = create_app()
