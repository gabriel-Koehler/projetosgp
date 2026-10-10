"""Correção das folhas de resposta (RF31 a RF40).

- ler_folha: só lê (OMR), não grava nada.
- corrigir: lê, calcula a nota e grava. Leitura duvidosa não é gravada (RN15).
- registrar_manual: grava respostas conferidas pelo professor (quando a leitura falha
  ou fica duvidosa, depois de ele conferir a folha).
"""

import uuid
from dataclasses import dataclass

import psycopg
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.database.connection import get_conn
from app.database.supabase_client import get_supabase, salvar_foto
from app.models.avaliacao import VersaoPorCodigo
from app.models.resultado import Resultado
from app.repositories.avaliacao_repository import AvaliacaoRepository
from app.repositories.cadastros_repository import AlunoRepository
from app.repositories.resultado_repository import ResultadoRepository
from app.services import omr_service
from app.services.errors import ErroDeNegocio, NaoEncontrado
from app.services.nota import ANULADA, calcular_nota
from app.services.omr_service import ErroLeitura, LeituraFolha, Situacao
from app.services.version_builder import indice_da_letra

TAMANHO_MAXIMO_FOTO = 15 * 1024 * 1024  # 15 MB


class LeituraInvalida(ErroDeNegocio):
    """Folha que não pôde ser lida (RF36, RF40): nada é registrado."""

    def __init__(self, erro: ErroLeitura) -> None:
        super().__init__(erro.mensagem, codigo=erro.codigo)


@dataclass
class LeituraCompleta:
    leitura: LeituraFolha
    versao: VersaoPorCodigo


def respostas_da_leitura(leitura: LeituraFolha) -> dict[int, str | None]:
    """Converte a leitura no formato gravado: letra, None (em branco) ou "*" (anulada)."""
    return {q.numero: ANULADA if q.situacao == Situacao.MULTIPLA else q.resposta for q in leitura.questoes}


class CorrecaoService:
    def __init__(self, conn: psycopg.Connection, settings: Settings, supabase=None) -> None:
        self.conn = conn
        self.settings = settings
        self.supabase = supabase
        self.avaliacoes = AvaliacaoRepository(conn)
        self.alunos = AlunoRepository(conn)
        self.resultados = ResultadoRepository(conn)

    def _versao_do_professor(self, professor_id: int, codigo: str) -> VersaoPorCodigo | None:
        versao = self.avaliacoes.obter_por_codigo(codigo)
        return versao if versao and versao.professor_id == professor_id else None

    def ler_folha(self, professor_id: int, conteudo: bytes) -> LeituraCompleta:
        """RF32 a RF36: identifica a versão pelo QR Code e lê as respostas marcadas."""
        if len(conteudo) > TAMANHO_MAXIMO_FOTO:
            raise ErroDeNegocio("Imagem muito grande (máximo 15 MB).")

        encontrada: dict[str, VersaoPorCodigo] = {}

        def alternativas_da_versao(codigo: str) -> dict[int, int]:
            versao = self._versao_do_professor(professor_id, codigo)
            if versao is None:
                raise ErroLeitura(
                    "prova_desconhecida",
                    "O QR Code desta folha não é de nenhuma das suas avaliações. Confira se é a folha certa.",
                )
            encontrada["versao"] = versao
            return versao.alternativas_por_questao

        try:
            leitura = omr_service.ler_folha(conteudo, alternativas_da_versao)
        except ErroLeitura as erro:
            raise LeituraInvalida(erro) from erro
        return LeituraCompleta(leitura=leitura, versao=encontrada["versao"])

    def corrigir(
        self, professor_id: int, conteudo: bytes, aluno_id: int | None = None, tipo_imagem: str = "image/jpeg"
    ) -> tuple[Resultado, LeituraCompleta]:
        """RF37 a RF40: lê, compara com o gabarito da versão, calcula a nota e grava."""
        completa = self.ler_folha(professor_id, conteudo)
        leitura, versao = completa.leitura, completa.versao
        if not leitura.confiavel:
            ilegiveis = leitura.numeros(Situacao.ILEGIVEL)
            raise ErroDeNegocio(
                f"Marcação duvidosa nas questões {', '.join(map(str, ilegiveis))}. "
                "Nada foi registrado: fotografe de novo ou confira a folha e registre manualmente.",
                codigo="leitura_duvidosa",
                dados={"codigo_versao": leitura.codigo, "ilegiveis": ilegiveis, "respostas": leitura.respostas},
            )
        self._validar_aluno(professor_id, versao, aluno_id)
        extensao = "png" if tipo_imagem == "image/png" else "jpg"
        imagem = salvar_foto(
            self.supabase, self.settings.supabase_bucket,
            f"avaliacao-{versao.avaliacao_id}/{uuid.uuid4().hex}.{extensao}", conteudo, tipo_imagem,
        )
        resultado = self._gravar(versao, aluno_id, respostas_da_leitura(leitura), "omr", imagem)
        return resultado, completa

    def registrar_manual(
        self, professor_id: int, codigo: str, respostas: dict[int, str | None], aluno_id: int | None = None
    ) -> Resultado:
        versao = self._versao_do_professor(professor_id, codigo)
        if versao is None:
            raise NaoEncontrado("Versão não encontrada. Confira o código da folha.")
        if set(respostas) != set(versao.gabarito):
            raise ErroDeNegocio(f"Informe a resposta das {len(versao.gabarito)} questões da versão (null = em branco).")

        normalizadas = {}
        for numero, resposta in respostas.items():
            valor = resposta.strip().upper() if resposta else None
            if valor not in (None, ANULADA):
                try:
                    if indice_da_letra(valor) >= versao.alternativas_por_questao[numero]:
                        raise ValueError
                except ValueError as erro:
                    raise ErroDeNegocio(f"Resposta '{resposta}' inválida na questão {numero}.") from erro
            normalizadas[numero] = valor
        self._validar_aluno(professor_id, versao, aluno_id)
        return self._gravar(versao, aluno_id, normalizadas, "manual", None)

    def _validar_aluno(self, professor_id: int, versao: VersaoPorCodigo, aluno_id: int | None) -> None:
        if aluno_id is None:
            return
        aluno = self.alunos.obter(professor_id, aluno_id)
        if not aluno:
            raise NaoEncontrado("Aluno não encontrado.")
        turma_id = self.conn.execute(
            "SELECT turma_id FROM avaliacao WHERE id = %s", (versao.avaliacao_id,)
        ).fetchone()["turma_id"]
        if turma_id is not None and aluno.turma_id != turma_id:
            raise ErroDeNegocio("O aluno não é da turma desta avaliação.")

    def _gravar(
        self, versao: VersaoPorCodigo, aluno_id: int | None, respostas: dict, origem: str, imagem: str | None
    ) -> Resultado:
        """RF38, RF39: nota e resultado com cópia das respostas e do gabarito."""
        nota = calcular_nota(respostas, versao.gabarito, versao.nota_maxima)
        resultado_id = self.resultados.salvar(
            versao.avaliacao_id, versao.versao_id, aluno_id, respostas, versao.gabarito, nota, origem, imagem
        )
        return self.resultados.obter(versao.professor_id, resultado_id)


def get_correcao_service(
    conn: psycopg.Connection = Depends(get_conn), settings: Settings = Depends(get_settings)
) -> CorrecaoService:
    return CorrecaoService(conn, settings, get_supabase())
