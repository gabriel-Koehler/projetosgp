"""Ponto de entrada da API: `uvicorn app.main:app --reload`."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import Settings, get_settings
from app.routers import aluno, auth, avaliacoes, painel


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="Sistema de Geração e Correção Automática de Avaliações",
        version="0.1.0",
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="sessao_professor",
        max_age=settings.session_max_age,
        same_site="lax",
        https_only=settings.session_https_only,
    )
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.dependency_overrides[get_settings] = lambda: settings

    app.include_router(auth.router)
    app.include_router(painel.router)
    app.include_router(avaliacoes.router)
    app.include_router(aluno.router)

    @app.get("/api/health", tags=["infra"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
