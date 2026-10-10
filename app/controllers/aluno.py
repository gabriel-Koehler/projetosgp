"""Consulta pública do gabarito pelo QR Code (RF29, RF30, RN03 a RN05).

Rota sem login. Devolve só o nome da avaliação/versão e as letras corretas:
nada de enunciados, respostas marcadas, notas ou estatísticas.
"""

from fastapi import APIRouter, Depends

from app.schemas.avaliacao import GabaritoAlunoOut, ItemGabarito
from app.services.avaliacao_service import AvaliacaoService, get_avaliacao_service

router = APIRouter(prefix="/student", tags=["aluno"])


@router.get("/gabarito/{codigo}", response_model=GabaritoAlunoOut)
def gabarito_da_versao(codigo: str, service: AvaliacaoService = Depends(get_avaliacao_service)):
    resultado = service.gabarito_do_aluno(codigo)
    return GabaritoAlunoOut(
        avaliacao=resultado.avaliacao,
        versao=resultado.versao,
        gabarito=[ItemGabarito(questao=n, alternativa=l) for n, l in resultado.gabarito.items()],
    )
