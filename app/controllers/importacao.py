"""Funções comuns às rotas de importação e aos modelos para download."""

from fastapi import Response

from app.schemas.cadastros import ErroLinhaOut, ImportacaoOut, LinhaValidaOut
from app.services.importacao import Previa

TIPOS = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def resposta_importacao(previa: Previa, importados: int, confirmar: bool) -> ImportacaoOut:
    return ImportacaoOut(
        confirmado=confirmar,
        total_linhas=previa.total,
        validas=[LinhaValidaOut(linha=l.linha, dados=l.dados) for l in previa.validas],
        erros=[ErroLinhaOut(linha=e.linha, mensagens=e.mensagens) for e in previa.erros],
        importados=importados,
    )


def arquivo(conteudo: bytes, nome: str) -> Response:
    extensao = nome.rsplit(".", 1)[-1]
    return Response(
        content=conteudo,
        media_type=TIPOS[extensao],
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )
