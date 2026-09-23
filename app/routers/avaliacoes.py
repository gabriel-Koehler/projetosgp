"""Criação de avaliações, geração das versões e QR Codes (RF14 a RF28).

Rotas administrativas: exigem o professor logado.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.core.qrcode_service import gerar_qrcode_png
from app.core.security import require_professor
from app.core.version_builder import ConfiguracaoVersoes, Nomenclatura, Questao, gerar_versoes
from app.mocks.avaliacoes_store import Avaliacao, AvaliacoesStore, get_store

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliações"], dependencies=[Depends(require_professor)])


class QuestaoIn(BaseModel):
    id: str = Field(min_length=1)
    enunciado: str = Field(min_length=1)
    alternativas: list[str] = Field(min_length=2, max_length=26)
    correta: str = Field(min_length=1, max_length=1)


class ConfiguracaoIn(BaseModel):
    quantidade: int = Field(ge=1, le=500)
    nomenclatura: Nomenclatura = Nomenclatura.LETRAS
    nomes_personalizados: list[str] = []
    mesmas_questoes: bool = True
    questoes_por_versao: int | None = Field(default=None, ge=1)
    embaralhar_questoes: bool = False
    embaralhar_alternativas: bool = False


class AvaliacaoIn(BaseModel):
    nome: str = Field(min_length=1)
    semestre: str | None = None
    turma: str | None = None
    # N1: as questões selecionadas vêm completas do front. Com o provedor
    # mock [N1-BE-02] / Supabase [N2-BE-03] passam a ser só os ids.
    questoes: list[QuestaoIn] = Field(min_length=1)
    configuracao: ConfiguracaoIn


class LiberarGabaritoIn(BaseModel):
    liberado: bool


class QuestaoVersaoOut(BaseModel):
    numero: int
    questao_id: str
    enunciado: str
    alternativas: list[str]
    correta: str
    ordem_original: list[str]


class VersaoOut(BaseModel):
    nome: str
    codigo: str
    url_aluno: str
    url_qrcode: str
    questoes: list[QuestaoVersaoOut]
    gabarito: dict[int, str]


class AvaliacaoOut(BaseModel):
    id: int
    nome: str
    semestre: str | None
    turma: str | None
    gabarito_liberado: bool
    versoes: list[VersaoOut]


def url_publica(request: Request, settings: Settings, caminho: str) -> str:
    base = settings.public_base_url or str(request.base_url)
    return base.rstrip("/") + caminho


def _serializar(avaliacao: Avaliacao, request: Request, settings: Settings) -> AvaliacaoOut:
    return AvaliacaoOut(
        id=avaliacao.id,
        nome=avaliacao.nome,
        semestre=avaliacao.semestre,
        turma=avaliacao.turma,
        gabarito_liberado=avaliacao.gabarito_liberado,
        versoes=[
            VersaoOut(
                nome=a.versao.nome,
                codigo=a.codigo,
                url_aluno=url_publica(request, settings, f"/student/gabarito/{a.codigo}"),
                url_qrcode=f"/api/avaliacoes/{avaliacao.id}/versoes/{a.codigo}/qrcode.png",
                questoes=[QuestaoVersaoOut(**vars(q)) for q in a.versao.questoes],
                gabarito=a.versao.gabarito,
            )
            for a in avaliacao.versoes
        ],
    )


def _obter_ou_404(store: AvaliacoesStore, avaliacao_id: int) -> Avaliacao:
    avaliacao = store.obter(avaliacao_id)
    if not avaliacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avaliação não encontrada.")
    return avaliacao


@router.post("", response_model=AvaliacaoOut, status_code=status.HTTP_201_CREATED)
def criar_avaliacao(
    dados: AvaliacaoIn,
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AvaliacoesStore = Depends(get_store),
):
    questoes = [Questao(**q.model_dump()) for q in dados.questoes]
    config = ConfiguracaoVersoes(**dados.configuracao.model_dump())
    try:
        versoes = gerar_versoes(questoes, config)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(erro)) from erro

    avaliacao = store.criar(dados.nome, dados.semestre, dados.turma, versoes)
    return _serializar(avaliacao, request, settings)


@router.get("", response_model=list[AvaliacaoOut])
def listar_avaliacoes(
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AvaliacoesStore = Depends(get_store),
):
    return [_serializar(a, request, settings) for a in store.listar()]


@router.get("/{avaliacao_id}", response_model=AvaliacaoOut)
def obter_avaliacao(
    avaliacao_id: int,
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AvaliacoesStore = Depends(get_store),
):
    return _serializar(_obter_ou_404(store, avaliacao_id), request, settings)


@router.patch("/{avaliacao_id}/gabarito", response_model=AvaliacaoOut)
def liberar_gabarito(
    avaliacao_id: int,
    dados: LiberarGabaritoIn,
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AvaliacoesStore = Depends(get_store),
):
    """Libera (ou bloqueia) a consulta do gabarito pelo QR Code."""
    avaliacao = _obter_ou_404(store, avaliacao_id)
    avaliacao.gabarito_liberado = dados.liberado
    return _serializar(avaliacao, request, settings)


@router.get("/{avaliacao_id}/versoes/{codigo}/qrcode.png", response_class=Response)
def qrcode_da_versao(
    avaliacao_id: int,
    codigo: str,
    request: Request,
    settings: Settings = Depends(get_settings),
    store: AvaliacoesStore = Depends(get_store),
):
    avaliacao = _obter_ou_404(store, avaliacao_id)
    if not any(a.codigo == codigo for a in avaliacao.versoes):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão não encontrada.")

    png = gerar_qrcode_png(url_publica(request, settings, f"/student/gabarito/{codigo}"))
    return Response(content=png, media_type="image/png")
