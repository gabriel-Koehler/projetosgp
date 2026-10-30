"""API unificada persistente: uvicorn app.persistent:create_app --factory."""

from contextlib import asynccontextmanager
import psycopg
from psycopg_pool import PoolTimeout

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import Settings, get_settings
from app.controllers import auth, cadastros, painel, questoes, avaliacoes, aluno, correcoes, resultados
from app.database.connection import obter_pool
from app.services.errors import ErroDeNegocio


def create_app(settings: Settings | None = None, *, development_login: bool = False) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        obter_pool(app, settings)
        try:
            yield
        finally:
            if getattr(app.state, "pool", None):
                app.state.pool.close()

    app = FastAPI(
        title="Sistema de Geração e Correção Automática de Avaliações",
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="sessao_professor" if development_login else "sessao_professor_n2",
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
    app.state.login_sem_banco = development_login

    @app.exception_handler(ErroDeNegocio)
    def erro_de_negocio(_: Request, erro: ErroDeNegocio):
        conteudo = {"detail": erro.mensagem, **erro.dados}
        if erro.codigo:
            conteudo["codigo"] = erro.codigo
        return JSONResponse(status_code=erro.status_code, content=jsonable_encoder(conteudo))

    @app.exception_handler(psycopg.OperationalError)
    @app.exception_handler(PoolTimeout)
    def banco_indisponivel(_: Request, erro: Exception):
        return JSONResponse(status_code=503, content={"detail": "Banco indisponível. Tente novamente em instantes."})

    app.include_router(auth.router)
    app.include_router(painel.router)
    app.include_router(cadastros.router)
    app.include_router(questoes.router)
    app.include_router(avaliacoes.router)
    app.include_router(aluno.router)
    app.include_router(correcoes.router)
    app.include_router(resultados.router)

    @app.get("/api/health", tags=["infra"])
    def health():
        pool = obter_pool(app, settings)
        if pool is None:
            if development_login:
                return {"status": "ok", "banco": "nao_configurado"}
            return JSONResponse(status_code=503, content={"status": "erro", "banco": "nao_configurado"})
        try:
            with pool.connection(timeout=5) as conn:
                conn.execute("SELECT 1")
        except Exception:
            return JSONResponse(status_code=503, content={"status": "erro", "banco": "indisponivel"})
        return {"status": "ok", "banco": "ok"}

    return app



