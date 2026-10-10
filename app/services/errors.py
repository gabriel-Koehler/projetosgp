"""Erros de regra de negócio. Os controllers os convertem em respostas HTTP (ver app/main.py)."""


class ErroDeNegocio(Exception):
    """Dados válidos no formato, mas que ferem uma regra (HTTP 422)."""

    status_code = 422

    def __init__(self, mensagem: str, codigo: str | None = None, dados: dict | None = None) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo  # identificador do motivo, para o front tratar (ex.: "leitura_duvidosa")
        self.dados = dados or {}  # informações extras devolvidas junto com o erro


class NaoEncontrado(ErroDeNegocio):
    status_code = 404


class AcessoNegado(ErroDeNegocio):
    status_code = 403


class Conflito(ErroDeNegocio):
    status_code = 409
