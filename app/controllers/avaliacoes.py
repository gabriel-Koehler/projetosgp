"""Rotas HTTP de avaliações, versões e QR Codes (RF14 a RF28). Exigem o professor logado."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, Request, Response, status

from app.core.config import Settings, get_settings
from app.core.security import professor_id
from app.models.avaliacao import Avaliacao
from app.schemas.avaliacao import (
    AvaliacaoIn,
    AvaliacaoOut,
    LiberarGabaritoIn,
    QuestaoVersaoOut,
    ResumoAvaliacaoOut,
    VersaoOut,
)
from app.services.avaliacao_service import AvaliacaoService, get_avaliacao_service
from app.services.qrcode_service import gerar_qrcode_png
from app.services.version_builder import ConfiguracaoVersoes

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliações"])

Service = Depends(get_avaliacao_service)
Professor = Depends(professor_id)


def url_publica(request: Request, settings: Settings, caminho: str) -> str:
    base = settings.public_base_url or str(request.base_url)
    return base.rstrip("/") + caminho


def url_do_aluno(request: Request, settings: Settings, codigo: str) -> str:
    return url_publica(request, settings, f"/student/gabarito/{codigo}")


def _serializar(avaliacao: Avaliacao, request: Request, settings: Settings) -> AvaliacaoOut:
    dados = {k: v for k, v in vars(avaliacao).items() if k != "versoes"}
    return AvaliacaoOut(
        **dados,
        versoes=[
            VersaoOut(
                id=v.id,
                nome=v.versao.nome,
                codigo=v.codigo,
                url_aluno=url_do_aluno(request, settings, v.codigo),
                url_qrcode=f"/api/avaliacoes/{avaliacao.id}/versoes/{v.codigo}/qrcode.png",
                questoes=[QuestaoVersaoOut(**vars(q)) for q in v.versao.questoes],
                gabarito=v.versao.gabarito,
            )
            for v in avaliacao.versoes
        ],
    )


@router.post("", response_model=AvaliacaoOut, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    dados: AvaliacaoIn,
    request: Request,
    settings: Settings = Depends(get_settings),
    prof: int = Professor,
    service: AvaliacaoService = Service,
):
    avaliacao = service.criar(
        prof,
        nome=dados.nome,
        turma_id=dados.turma_id,
        questao_ids=dados.questao_ids,
        config=ConfiguracaoVersoes(**dados.configuracao.model_dump()),
        nota_maxima=dados.nota_maxima,
        gabaritos=dados.gabaritos,
    )
    return _serializar(avaliacao, request, settings)


@router.get("", response_model=list[ResumoAvaliacaoOut])
def listar_avaliacoes(turma_id: int | None = None, prof: int = Professor, service: AvaliacaoService = Service):
    return [asdict(a) for a in service.listar(prof, turma_id)]


@router.get("/{avaliacao_id}", response_model=AvaliacaoOut)
def obter_avaliacao(
    avaliacao_id: int,
    request: Request,
    settings: Settings = Depends(get_settings),
    prof: int = Professor,
    service: AvaliacaoService = Service,
):
    return _serializar(service.obter(prof, avaliacao_id), request, settings)


@router.delete("/{avaliacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_avaliacao(avaliacao_id: int, prof: int = Professor, service: AvaliacaoService = Service):
    """Só é possível antes de corrigir alguma prova."""
    service.excluir(prof, avaliacao_id)


@router.patch("/{avaliacao_id}/gabarito", response_model=AvaliacaoOut)
def liberar_gabarito(
    avaliacao_id: int,
    dados: LiberarGabaritoIn,
    request: Request,
    settings: Settings = Depends(get_settings),
    prof: int = Professor,
    service: AvaliacaoService = Service,
):
    """Libera (ou bloqueia) a consulta do gabarito pelo QR Code."""
    return _serializar(service.liberar_gabarito(prof, avaliacao_id, dados.liberado), request, settings)


@router.get("/{avaliacao_id}/versoes/{codigo}/qrcode.png", response_class=Response)
def qrcode_da_versao(
    avaliacao_id: int,
    codigo: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    prof: int = Professor,
    service: AvaliacaoService = Service,
):
    service.obter_versao(prof, avaliacao_id, codigo)
    png = gerar_qrcode_png(url_do_aluno(request, settings, codigo))
    return Response(content=png, media_type="image/png")
