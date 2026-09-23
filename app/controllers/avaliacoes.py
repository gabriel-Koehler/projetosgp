"""Rotas HTTP de avaliações, versões e QR Codes (RF14 a RF28). Exigem o professor logado."""

from fastapi import APIRouter, Depends, Request, Response, status

from app.core.config import Settings, get_settings
from app.core.security import require_professor
from app.models.avaliacao import Avaliacao
from app.schemas.avaliacao import AvaliacaoIn, AvaliacaoOut, LiberarGabaritoIn, QuestaoVersaoOut, VersaoOut
from app.services.avaliacao_service import AvaliacaoService, get_avaliacao_service
from app.services.qrcode_service import gerar_qrcode_png
from app.services.version_builder import ConfiguracaoVersoes, Questao

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliações"], dependencies=[Depends(require_professor)])


def url_publica(request: Request, settings: Settings, caminho: str) -> str:
    base = settings.public_base_url or str(request.base_url)
    return base.rstrip("/") + caminho


def url_do_aluno(request: Request, settings: Settings, codigo: str) -> str:
    return url_publica(request, settings, f"/student/gabarito/{codigo}")


def _serializar(avaliacao: Avaliacao, request: Request, settings: Settings) -> AvaliacaoOut:
    return AvaliacaoOut(
        id=avaliacao.id,
        nome=avaliacao.nome,
        semestre=avaliacao.semestre,
        turma=avaliacao.turma,
        gabarito_liberado=avaliacao.gabarito_liberado,
        versoes=[
            VersaoOut(
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
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    avaliacao = service.criar(
        nome=dados.nome,
        semestre=dados.semestre,
        turma=dados.turma,
        questoes=[Questao(**q.model_dump()) for q in dados.questoes],
        config=ConfiguracaoVersoes(**dados.configuracao.model_dump()),
    )
    return _serializar(avaliacao, request, settings)


@router.get("", response_model=list[AvaliacaoOut])
def listar_avaliacoes(
    request: Request,
    settings: Settings = Depends(get_settings),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    return [_serializar(a, request, settings) for a in service.listar()]


@router.get("/{avaliacao_id}", response_model=AvaliacaoOut)
def obter_avaliacao(
    avaliacao_id: int,
    request: Request,
    settings: Settings = Depends(get_settings),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    return _serializar(service.obter(avaliacao_id), request, settings)


@router.patch("/{avaliacao_id}/gabarito", response_model=AvaliacaoOut)
def liberar_gabarito(
    avaliacao_id: int,
    dados: LiberarGabaritoIn,
    request: Request,
    settings: Settings = Depends(get_settings),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    """Libera (ou bloqueia) a consulta do gabarito pelo QR Code."""
    return _serializar(service.liberar_gabarito(avaliacao_id, dados.liberado), request, settings)


@router.get("/{avaliacao_id}/versoes/{codigo}/qrcode.png", response_class=Response)
def qrcode_da_versao(
    avaliacao_id: int,
    codigo: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    service.obter_versao(avaliacao_id, codigo)
    png = gerar_qrcode_png(url_do_aluno(request, settings, codigo))
    return Response(content=png, media_type="image/png")
