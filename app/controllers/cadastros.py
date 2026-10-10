"""Rotas de semestres (RF02), turmas (RF03) e alunos (RF04, RF05). Exigem o professor logado."""

from typing import Literal

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.controllers.importacao import arquivo, resposta_importacao
from app.core.security import professor_id
from app.schemas.cadastros import AlunoIn, AlunoOut, AtivoIn, ImportacaoOut, SemestreIn, SemestreOut, TurmaIn, TurmaOut
from app.services import importacao
from app.services.cadastros_service import CadastrosService, get_cadastros_service

router = APIRouter(prefix="/api", tags=["semestres, turmas e alunos"])

Service = Depends(get_cadastros_service)
Professor = Depends(professor_id)


# --- Semestres ---------------------------------------------------------------------


@router.get("/semestres", response_model=list[SemestreOut])
def listar_semestres(ativo: bool | None = None, prof: int = Professor, service: CadastrosService = Service):
    return service.listar_semestres(prof, ativo)


@router.post("/semestres", response_model=SemestreOut, status_code=status.HTTP_201_CREATED)
def criar_semestre(dados: SemestreIn, prof: int = Professor, service: CadastrosService = Service):
    return service.criar_semestre(prof, dados.nome, dados.data_inicio, dados.data_fim)


@router.get("/semestres/{semestre_id}", response_model=SemestreOut)
def obter_semestre(semestre_id: int, prof: int = Professor, service: CadastrosService = Service):
    return service.obter_semestre(prof, semestre_id)


@router.put("/semestres/{semestre_id}", response_model=SemestreOut)
def atualizar_semestre(semestre_id: int, dados: SemestreIn, prof: int = Professor, service: CadastrosService = Service):
    return service.atualizar_semestre(prof, semestre_id, dados.nome, dados.data_inicio, dados.data_fim)


@router.patch("/semestres/{semestre_id}/ativo", response_model=SemestreOut)
def ativar_semestre(semestre_id: int, dados: AtivoIn, prof: int = Professor, service: CadastrosService = Service):
    return service.definir_semestre_ativo(prof, semestre_id, dados.ativo)


# --- Turmas ------------------------------------------------------------------------


@router.get("/turmas", response_model=list[TurmaOut])
def listar_turmas(semestre_id: int | None = None, prof: int = Professor, service: CadastrosService = Service):
    return service.listar_turmas(prof, semestre_id)


@router.post("/turmas", response_model=TurmaOut, status_code=status.HTTP_201_CREATED)
def criar_turma(dados: TurmaIn, prof: int = Professor, service: CadastrosService = Service):
    return service.criar_turma(prof, dados.semestre_id, dados.nome, dados.disciplina)


@router.get("/turmas/{turma_id}", response_model=TurmaOut)
def obter_turma(turma_id: int, prof: int = Professor, service: CadastrosService = Service):
    return service.obter_turma(prof, turma_id)


@router.put("/turmas/{turma_id}", response_model=TurmaOut)
def atualizar_turma(turma_id: int, dados: TurmaIn, prof: int = Professor, service: CadastrosService = Service):
    return service.atualizar_turma(prof, turma_id, dados.semestre_id, dados.nome, dados.disciplina)


@router.delete("/turmas/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_turma(turma_id: int, prof: int = Professor, service: CadastrosService = Service):
    service.excluir_turma(prof, turma_id)


# --- Alunos ------------------------------------------------------------------------


@router.get("/alunos/modelo.{formato}", tags=["importação"])
def modelo_alunos(formato: Literal["csv", "xlsx"], _: int = Professor):
    """RF05: modelo de planilha para importar alunos."""
    gerar = importacao.modelo_csv if formato == "csv" else importacao.modelo_xlsx
    return arquivo(gerar(importacao.COLUNAS_ALUNO, importacao.EXEMPLO_ALUNO), f"modelo_alunos.{formato}")


@router.get("/turmas/{turma_id}/alunos", response_model=list[AlunoOut])
def listar_alunos(turma_id: int, prof: int = Professor, service: CadastrosService = Service):
    return service.listar_alunos(prof, turma_id)


@router.post("/turmas/{turma_id}/alunos", response_model=AlunoOut, status_code=status.HTTP_201_CREATED)
def criar_aluno(turma_id: int, dados: AlunoIn, prof: int = Professor, service: CadastrosService = Service):
    return service.criar_aluno(prof, turma_id, dados.nome, dados.matricula, dados.email)


@router.post("/turmas/{turma_id}/alunos/importar", response_model=ImportacaoOut, tags=["importação"])
async def importar_alunos(
    turma_id: int,
    arquivo_planilha: UploadFile = File(alias="arquivo"),
    confirmar: bool = Query(False, description="false = só prévia; true = grava as linhas válidas"),
    prof: int = Professor,
    service: CadastrosService = Service,
):
    conteudo = await arquivo_planilha.read()
    previa, importados = service.importar_alunos(prof, turma_id, conteudo, arquivo_planilha.filename or "", confirmar)
    return resposta_importacao(previa, importados, confirmar)


@router.get("/alunos/{aluno_id}", response_model=AlunoOut)
def obter_aluno(aluno_id: int, prof: int = Professor, service: CadastrosService = Service):
    return service.obter_aluno(prof, aluno_id)


@router.put("/alunos/{aluno_id}", response_model=AlunoOut)
def atualizar_aluno(aluno_id: int, dados: AlunoIn, prof: int = Professor, service: CadastrosService = Service):
    return service.atualizar_aluno(prof, aluno_id, dados.nome, dados.matricula, dados.email)


@router.delete("/alunos/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(aluno_id: int, prof: int = Professor, service: CadastrosService = Service):
    service.excluir_aluno(prof, aluno_id)
