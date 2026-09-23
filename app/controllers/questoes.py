"""Rotas do banco de questões (RF06 a RF13). Exigem o professor logado."""

from typing import Literal

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.controllers.importacao import arquivo, resposta_importacao
from app.core.security import professor_id
from app.schemas.cadastros import (
    ExclusaoQuestaoOut,
    FiltrosQuestoes,
    ImportacaoOut,
    PaginaQuestoes,
    QuestaoIn,
    QuestaoOut,
)
from app.services import importacao
from app.services.questao_service import QuestaoService, get_questao_service

router = APIRouter(prefix="/api/questoes", tags=["banco de questões"])

Service = Depends(get_questao_service)
Professor = Depends(professor_id)


@router.get("", response_model=PaginaQuestoes)
def buscar_questoes(
    busca: str | None = Query(None, description="Texto no enunciado ou nas alternativas"),
    disciplina: str | None = None,
    categoria: str | None = None,
    dificuldade: Literal["facil", "media", "dificil"] | None = None,
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=200),
    prof: int = Professor,
    service: QuestaoService = Service,
):
    """RF09: pesquisar e filtrar o banco de questões."""
    itens, total = service.buscar(
        prof, pagina, por_pagina, texto=busca, disciplina=disciplina, categoria=categoria, dificuldade=dificuldade
    )
    return PaginaQuestoes(itens=[vars(q) for q in itens], total=total, pagina=pagina, por_pagina=por_pagina)


@router.get("/filtros", response_model=FiltrosQuestoes)
def filtros(prof: int = Professor, service: QuestaoService = Service):
    """Disciplinas e categorias já usadas, para montar os filtros da tela."""
    return service.filtros(prof)


@router.get("/modelo.{formato}", tags=["importação"])
def modelo_questoes(formato: Literal["csv", "xlsx"], _: int = Professor):
    """RF13: modelo de planilha para importar questões."""
    gerar = importacao.modelo_csv if formato == "csv" else importacao.modelo_xlsx
    return arquivo(gerar(importacao.COLUNAS_QUESTAO, importacao.EXEMPLO_QUESTAO), f"modelo_questoes.{formato}")


@router.post("/importar", response_model=ImportacaoOut, tags=["importação"])
async def importar_questoes(
    arquivo_planilha: UploadFile = File(alias="arquivo"),
    confirmar: bool = Query(False, description="false = só prévia; true = grava as linhas válidas"),
    prof: int = Professor,
    service: QuestaoService = Service,
):
    """RF10 a RF12: valida a planilha e mostra a prévia; com confirmar=true, grava as válidas."""
    conteudo = await arquivo_planilha.read()
    previa, importadas = service.importar(prof, conteudo, arquivo_planilha.filename or "", confirmar)
    return resposta_importacao(previa, importadas, confirmar)


@router.post("", response_model=QuestaoOut, status_code=status.HTTP_201_CREATED)
def criar_questao(dados: QuestaoIn, prof: int = Professor, service: QuestaoService = Service):
    return vars(service.criar(prof, dados.model_dump()))


@router.get("/{questao_id}", response_model=QuestaoOut)
def obter_questao(questao_id: int, prof: int = Professor, service: QuestaoService = Service):
    return vars(service.obter(prof, questao_id))


@router.put("/{questao_id}", response_model=QuestaoOut)
def atualizar_questao(questao_id: int, dados: QuestaoIn, prof: int = Professor, service: QuestaoService = Service):
    return vars(service.atualizar(prof, questao_id, dados.model_dump()))


@router.delete("/{questao_id}", response_model=ExclusaoQuestaoOut)
def excluir_questao(questao_id: int, prof: int = Professor, service: QuestaoService = Service):
    """RF08: questão já usada em avaliação é arquivada em vez de apagada."""
    return vars(service.excluir(prof, questao_id))
