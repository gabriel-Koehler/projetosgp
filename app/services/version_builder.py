"""Geração das versões de uma avaliação (RF17 a RF25, RN06 a RN11).

Função pura: não acessa banco nem estado global. Recebe as questões
selecionadas e a configuração, e devolve as versões com o gabarito de cada uma.

O embaralhamento trabalha com posições (índices), nunca com o texto das
alternativas, então alternativas com texto repetido não confundem o gabarito.
"""

import random
from dataclasses import dataclass, field
from enum import Enum

CORES = ["Azul", "Verde", "Amarela", "Vermelha", "Branca", "Rosa", "Laranja", "Roxa", "Cinza", "Marrom"]


class Nomenclatura(str, Enum):
    LETRAS = "letras"  # A, B, C, ..., Z, AA, AB
    NUMEROS = "numeros"  # 1, 2, 3
    CORES = "cores"  # Azul, Verde, Amarela
    PERSONALIZADA = "personalizada"


@dataclass(frozen=True)
class Questao:
    id: str
    enunciado: str
    alternativas: list[str]
    correta: str  # letra no banco de questões: "A", "B", ...


@dataclass(frozen=True)
class ConfiguracaoVersoes:
    quantidade: int
    nomenclatura: Nomenclatura = Nomenclatura.LETRAS
    nomes_personalizados: list[str] = field(default_factory=list)
    mesmas_questoes: bool = True
    # Só usado com mesmas_questoes=False; None = todas as questões em cada versão.
    questoes_por_versao: int | None = None
    embaralhar_questoes: bool = False
    embaralhar_alternativas: bool = False


@dataclass(frozen=True)
class QuestaoVersao:
    numero: int  # posição na prova, começando em 1
    questao_id: str | None  # None se a questão foi excluída do banco depois
    enunciado: str
    alternativas: list[str]  # na ordem em que aparecem nesta versão
    correta: str  # letra correta nesta versão
    # Letra original (no banco) de cada alternativa exibida. Ex.: ["C", "A", "D", "B"]
    # significa que a alternativa A desta versão é a C do banco.
    ordem_original: list[str]


@dataclass(frozen=True)
class Versao:
    nome: str
    questoes: list[QuestaoVersao]

    @property
    def gabarito(self) -> dict[int, str]:
        return {q.numero: q.correta for q in self.questoes}


def letra(indice: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    resultado = ""
    indice += 1
    while indice:
        indice, resto = divmod(indice - 1, 26)
        resultado = chr(65 + resto) + resultado
    return resultado


def indice_da_letra(valor: str) -> int:
    valor = valor.strip().upper()
    if len(valor) != 1 or not "A" <= valor <= "Z":
        raise ValueError(f"Gabarito inválido: '{valor}'. Use uma letra (A, B, C...).")
    return ord(valor) - 65


def nomes_das_versoes(config: ConfiguracaoVersoes) -> list[str]:
    n = config.quantidade
    if config.nomenclatura == Nomenclatura.LETRAS:
        return [letra(i) for i in range(n)]
    if config.nomenclatura == Nomenclatura.NUMEROS:
        return [str(i + 1) for i in range(n)]
    if config.nomenclatura == Nomenclatura.CORES:
        # Mais versões que cores: repete a lista com sufixo (Azul 2, Verde 2...).
        return [CORES[i % len(CORES)] + (f" {i // len(CORES) + 1}" if i >= len(CORES) else "") for i in range(n)]

    nomes = [nome.strip() for nome in config.nomes_personalizados]
    if len(nomes) != n or any(not nome for nome in nomes):
        raise ValueError(f"Informe exatamente {n} nome(s) de versão, sem nomes vazios.")
    if len({nome.casefold() for nome in nomes}) != n:
        raise ValueError("Os nomes das versões não podem se repetir.")
    return nomes


def _validar(questoes: list[Questao], config: ConfiguracaoVersoes) -> None:
    if config.quantidade < 1:
        raise ValueError("A quantidade de versões deve ser pelo menos 1.")
    if not questoes:
        raise ValueError("Selecione pelo menos uma questão.")
    ids = [q.id for q in questoes]
    if len(set(ids)) != len(ids):
        raise ValueError("A mesma questão foi selecionada mais de uma vez.")
    for q in questoes:
        if len(q.alternativas) < 2:
            raise ValueError(f"A questão {q.id} precisa de pelo menos 2 alternativas.")
        if indice_da_letra(q.correta) >= len(q.alternativas):
            raise ValueError(f"O gabarito da questão {q.id} aponta para uma alternativa inexistente.")
    if not config.mesmas_questoes and config.questoes_por_versao is not None:
        if not 1 <= config.questoes_por_versao <= len(questoes):
            raise ValueError(
                f"Questões por versão deve estar entre 1 e {len(questoes)} (total selecionado)."
            )


def _conjuntos_diferentes(questoes: list[Questao], n: int, por_versao: int, rng: random.Random) -> list[list[Questao]]:
    """Distribui as questões entre as versões (RF20).

    Percorre o banco embaralhado de forma circular: se houver questões
    suficientes (n * por_versao), os conjuntos não se repetem; se não houver,
    as repetições ficam distribuídas por igual entre as versões.
    """
    banco = list(questoes)
    rng.shuffle(banco)
    posicao_original = {q.id: i for i, q in enumerate(questoes)}
    conjuntos = []
    for v in range(n):
        inicio = v * por_versao
        conjunto = [banco[(inicio + i) % len(banco)] for i in range(por_versao)]
        # Sem embaralhar questões, a versão mantém a ordem do banco.
        conjunto.sort(key=lambda q: posicao_original[q.id])
        conjuntos.append(conjunto)
    return conjuntos


def _montar_questao(numero: int, questao: Questao, embaralhar: bool, rng: random.Random) -> QuestaoVersao:
    ordem = list(range(len(questao.alternativas)))
    if embaralhar:
        rng.shuffle(ordem)
    indice_correto = indice_da_letra(questao.correta)
    return QuestaoVersao(
        numero=numero,
        questao_id=questao.id,
        enunciado=questao.enunciado,
        alternativas=[questao.alternativas[i] for i in ordem],
        correta=letra(ordem.index(indice_correto)),
        ordem_original=[letra(i) for i in ordem],
    )


def gerar_versoes(
    questoes: list[Questao],
    config: ConfiguracaoVersoes,
    seed: int | None = None,
) -> list[Versao]:
    """Gera as versões da avaliação.

    `seed` torna o resultado reproduzível (usado nos testes e para regerar
    uma versão igual à original).
    """
    _validar(questoes, config)
    rng = random.Random(seed)
    nomes = nomes_das_versoes(config)

    if config.mesmas_questoes:
        conjuntos = [list(questoes) for _ in nomes]
    else:
        por_versao = config.questoes_por_versao or len(questoes)
        conjuntos = _conjuntos_diferentes(questoes, len(nomes), por_versao, rng)

    versoes = []
    for nome, conjunto in zip(nomes, conjuntos):
        if config.embaralhar_questoes:
            rng.shuffle(conjunto)
        versoes.append(
            Versao(
                nome=nome,
                questoes=[
                    _montar_questao(numero, questao, config.embaralhar_alternativas, rng)
                    for numero, questao in enumerate(conjunto, start=1)
                ],
            )
        )
    return versoes
