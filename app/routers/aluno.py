"""Consulta pública do gabarito pelo QR Code (RF29, RF30, RN03 a RN05).

Rota sem login. Devolve só o nome da avaliação/versão e as letras corretas:
nada de enunciados, respostas marcadas, notas ou estatísticas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.mocks.avaliacoes_store import AvaliacoesStore, get_store

router = APIRouter(prefix="/student", tags=["aluno"])


class ItemGabarito(BaseModel):
    questao: int
    alternativa: str


class GabaritoAlunoOut(BaseModel):
    avaliacao: str
    versao: str
    gabarito: list[ItemGabarito]


@router.get("/gabarito/{codigo}", response_model=GabaritoAlunoOut)
def gabarito_da_versao(codigo: str, store: AvaliacoesStore = Depends(get_store)):
    encontrado = store.obter_por_codigo(codigo)
    if not encontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gabarito não encontrado. Confira o QR Code.")

    avaliacao, armazenada = encontrado
    if not avaliacao.gabarito_liberado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O gabarito desta prova ainda não foi liberado pelo professor.",
        )

    return GabaritoAlunoOut(
        avaliacao=avaliacao.nome,
        versao=armazenada.versao.nome,
        gabarito=[ItemGabarito(questao=n, alternativa=l) for n, l in armazenada.versao.gabarito.items()],
    )
