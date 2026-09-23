"""Ponto de entrada da API: `uvicorn app.main:app --reload`."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import Settings, get_settings
from app.controllers import aluno, auth, avaliacoes, painel
from app.database.connection import criar_pool
from app.services.errors import ErroDeNegocio


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.pool = criar_pool(settings.database_url) if settings.database_url else None
        yield
        if app.state.pool:
            app.state.pool.close()

    app = FastAPI(
        title="Sistema de Geração e Correção Automática de Avaliações",
        version="0.2.0",
        lifespan=lifespan,
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

    @app.exception_handler(ErroDeNegocio)
    def erro_de_negocio(_: Request, erro: ErroDeNegocio):
        return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})

    app.include_router(auth.router)
    app.include_router(painel.router)
    app.include_router(avaliacoes.router)
    app.include_router(aluno.router)

    @app.get("/api/health", tags=["infra"])
    def health():
        pool = getattr(app.state, "pool", None)
        if pool is None:
            return {"status": "ok", "banco": "nao_configurado"}
        try:
            with pool.connection(timeout=5) as conn:
                conn.execute("SELECT 1")
        except Exception:
            return JSONResponse(status_code=503, content={"status": "erro", "banco": "indisponivel"})
        return {"status": "ok", "banco": "ok"}

    return app


app = create_app()
