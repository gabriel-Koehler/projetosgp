"""Rotas de resultados, estatísticas e relatório Excel (RF41 a RF48). Exigem o professor logado."""

import re
import unicodedata
from dataclasses import asdict

from fastapi import APIRouter, Depends, Response, status

from app.controllers.correcoes import resultado_out
from app.core.security import professor_id
from app.schemas.correcao import EstatisticasOut, ResultadoOut
from app.services.resultado_service import ResultadoService, get_resultado_service

router = APIRouter(prefix="/api", tags=["resultados e relatórios"])

Service = Depends(get_resultado_service)
Professor = Depends(professor_id)
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/avaliacoes/{avaliacao_id}/resultados", response_model=list[ResultadoOut])
def listar_resultados(avaliacao_id: int, prof: int = Professor, service: ResultadoService = Service):
    """RF41: resultados da avaliação, com a nota e as respostas de cada aluno."""
    return [resultado_out(r) for r in service.listar(prof, avaliacao_id)]


@router.get("/avaliacoes/{avaliacao_id}/estatisticas", response_model=EstatisticasOut)
def estatisticas(avaliacao_id: int, prof: int = Professor, service: ResultadoService = Service):
    """RF44 a RF46: por questão (escolhas por alternativa, mais escolhida) e da turma (média, distribuição)."""
    return asdict(service.estatisticas(prof, avaliacao_id))


@router.get("/avaliacoes/{avaliacao_id}/resultados.xlsx", response_class=Response)
def exportar_excel(avaliacao_id: int, prof: int = Professor, service: ResultadoService = Service):
    """RF47, RF48: planilha com resultados, estatísticas por questão e resumo da turma."""
    nome, conteudo = service.relatorio_excel(prof, avaliacao_id)
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    arquivo = re.sub(r"[^A-Za-z0-9]+", "_", f"resultados_{sem_acento}").strip("_") + ".xlsx"
    return Response(
        content=conteudo, media_type=XLSX, headers={"Content-Disposition": f'attachment; filename="{arquivo}"'}
    )


@router.get("/resultados/{resultado_id}", response_model=ResultadoOut)
def obter_resultado(resultado_id: int, prof: int = Professor, service: ResultadoService = Service):
    """RF42, RF43: questão, alternativa marcada, correta, situação e nota."""
    return resultado_out(service.obter(prof, resultado_id))


@router.delete("/resultados/{resultado_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_resultado(resultado_id: int, prof: int = Professor, service: ResultadoService = Service):
    service.excluir(prof, resultado_id)
