"""Hash de senha com PBKDF2-SHA256 (biblioteca padrão, sem dependências extras)."""

import hashlib
import hmac
import secrets

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000


def gerar_hash(senha: str, iteracoes: int = ITERACOES) -> str:
    sal = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), iteracoes).hex()
    return f"{ALGORITMO}${iteracoes}${sal}${digest}"


def verificar(senha: str, hash_salvo: str) -> bool:
    try:
        algoritmo, iteracoes, sal, digest = hash_salvo.split("$")
    except ValueError:
        return False
    if algoritmo != ALGORITMO:
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal.encode(), int(iteracoes)).hex()
    return hmac.compare_digest(calculado, digest)
