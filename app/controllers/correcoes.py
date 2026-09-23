"""Rotas de correção das folhas de resposta (RF31 a RF40). Exigem o professor logado."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.security import professor_id
from app.schemas.correcao import LeituraOut, QuestaoLidaOut
from app.services.correcao_service import CorrecaoService, LeituraCompleta, get_correcao_service
from app.services.omr_service import Situacao

router = APIRouter(prefix="/api/correcoes", tags=["correção"])

Service = Depends(get_correcao_service)
Professor = Depends(professor_id)


def mensagem_da_leitura(leitura) -> str:
    if not leitura.confiavel:
        numeros = ", ".join(map(str, leitura.numeros(Situacao.ILEGIVEL)))
        return f"Marcação duvidosa nas questões {numeros}. Fotografe de novo ou confira manualmente."
    avisos = []
    if em_branco := leitura.numeros(Situacao.EM_BRANCO):
        avisos.append(f"em branco: {', '.join(map(str, em_branco))}")
    if multiplas := leitura.numeros(Situacao.MULTIPLA):
        avisos.append(f"mais de uma marcação (anuladas): {', '.join(map(str, multiplas))}")
    return "Leitura concluída." + (f" Questões {'; '.join(avisos)}." if avisos else "")


def leitura_out(completa: LeituraCompleta) -> LeituraOut:
    leitura, versao = completa.leitura, completa.versao
    return LeituraOut(
        codigo=leitura.codigo,
        avaliacao_id=versao.avaliacao_id,
        avaliacao=versao.avaliacao_nome,
        versao=versao.versao_nome,
        confiavel=leitura.confiavel,
        mensagem=mensagem_da_leitura(leitura),
        respostas=leitura.respostas,
        em_branco=leitura.numeros(Situacao.EM_BRANCO),
        multiplas=leitura.numeros(Situacao.MULTIPLA),
        ilegiveis=leitura.numeros(Situacao.ILEGIVEL),
        questoes=[QuestaoLidaOut(**vars(q)) for q in leitura.questoes],
    )


@router.post("/leitura", response_model=LeituraOut)
async def ler_folha(
    imagem: UploadFile = File(description="Foto ou scan da folha de respostas (JPG ou PNG)"),
    prof: int = Professor,
    service: CorrecaoService = Service,
):
    """Lê a folha sem registrar nada: identifica a versão pelo QR Code e as alternativas marcadas.

    Folha fora do padrão, QR Code ilegível ou prova desconhecida respondem 422 com `codigo` e `detail`.
    """
    return leitura_out(service.ler_folha(prof, await imagem.read()))
