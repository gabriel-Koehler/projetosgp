"""Painel do professor: exemplo de router administrativo protegido.

Todo router administrativo deve declarar `dependencies=[Depends(require_professor)]`.
"""

from fastapi import APIRouter, Depends

from app.core.security import require_professor

router = APIRouter(prefix="/api/painel", tags=["painel"], dependencies=[Depends(require_professor)])


@router.get("")
def painel(professor: dict = Depends(require_professor)):
    return {"professor": professor}
