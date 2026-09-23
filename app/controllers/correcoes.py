"""Rotas de correção das folhas de resposta (RF31 a RF40). Exigem o professor logado."""

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.security import professor_id
from app.models.resultado import Resultado
from app.schemas.correcao import (
    CorrecaoManualIn,
    CorrecaoOut,
    LeituraOut,
    QuestaoLidaOut,
    QuestaoResultadoOut,
    ResultadoOut,
)
from app.services.correcao_service import CorrecaoService, LeituraCompleta, get_correcao_service
from app.services.nota import situacao
from app.services.omr_service import Situacao

router = APIRouter(prefix="/api/correcoes", tags=["correção"])

Service = Depends(get_correcao_service)
Professor = Depends(professor_id)


def resultado_out(resultado: Resultado) -> ResultadoOut:
    """RF42, RF43: nota e, por questão, a alternativa marcada, a correta e a situação."""
    dados = {k: v for k, v in vars(resultado).items() if k not in ("respostas", "gabarito", "imagem_path")}
    return ResultadoOut(
        **dados,
        questoes=[
            QuestaoResultadoOut(
                numero=n, marcada=resultado.respostas.get(n), correta=correta,
                situacao=situacao(resultado.respostas.get(n), correta),
            )
            for n, correta in sorted(resultado.gabarito.items())
        ],
    )


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


@router.post("", response_model=CorrecaoOut, status_code=status.HTTP_201_CREATED)
async def corrigir_prova(
    imagem: UploadFile = File(description="Foto ou scan da folha de respostas (JPG ou PNG)"),
    aluno_id: int | None = Form(None, description="Aluno dono da folha (opcional)"),
    prof: int = Professor,
    service: CorrecaoService = Service,
):
    """RF31 a RF40: lê a folha, compara com o gabarito da versão, calcula a nota e grava o resultado.

    Se alguma marcação ficar duvidosa, **nada é gravado**: responde 422 com `codigo: "leitura_duvidosa"`,
    as questões `ilegiveis` e as `respostas` lidas, para o professor fotografar de novo ou conferir e
    registrar em `POST /api/correcoes/manual`. O mesmo aluno corrigido de novo substitui o resultado anterior.
    """
    conteudo = await imagem.read()
    resultado, completa = service.corrigir(prof, conteudo, aluno_id, imagem.content_type or "image/jpeg")
    return CorrecaoOut(resultado=resultado_out(resultado), leitura=leitura_out(completa))


@router.post("/manual", response_model=ResultadoOut, status_code=status.HTTP_201_CREATED)
def registrar_manual(dados: CorrecaoManualIn, prof: int = Professor, service: CorrecaoService = Service):
    """Registra respostas conferidas pelo professor (quando a leitura automática falha ou fica duvidosa)."""
    return resultado_out(service.registrar_manual(prof, dados.codigo, dados.respostas, dados.aluno_id))
