"""Teste de conectividade com o banco e o Storage do Supabase.

Uso: `python -m app.database.check`
"""

from app.core.config import Settings, get_settings
from app.database.connection import conectar
from app.database.supabase_client import criar_cliente_supabase

TABELAS = [
    "professor", "semestre", "turma", "aluno", "questao", "alternativa", "avaliacao",
    "avaliacao_questao", "versao_avaliacao", "questao_versao", "gabarito_versao", "resultado_correcao",
]


def verificar_banco(settings: Settings) -> dict:
    with conectar(settings.database_url) as conn:
        versao = conn.execute("SELECT version() AS v").fetchone()["v"]
        existentes = {
            linha["table_name"]
            for linha in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()"
            )
        }
    return {"versao": versao, "tabelas_faltando": [t for t in TABELAS if t not in existentes]}


def main(settings: Settings) -> None:
    if not settings.database_url:
        raise SystemExit("[ERRO] DATABASE_URL não definida.")

    resultado = verificar_banco(settings)
    print(f"[OK] Conectado: {resultado['versao'].split(',')[0]}")
    if resultado["tabelas_faltando"]:
        print(f"[AVISO] Tabelas faltando: {', '.join(resultado['tabelas_faltando'])} (rode python -m app.database.migrate)")
    else:
        print(f"[OK] As {len(TABELAS)} tabelas existem.")

    cliente = criar_cliente_supabase(settings)
    if cliente is None:
        print("[INFO] Supabase Storage não configurado (SUPABASE_URL / SUPABASE_KEY): fotos das folhas não serão guardadas.")
    else:
        buckets = [b.name for b in cliente.storage.list_buckets()]
        status = "[OK]" if settings.supabase_bucket in buckets else "[AVISO] não encontrado:"
        print(f"{status} bucket '{settings.supabase_bucket}' no Storage.")


if __name__ == "__main__":
    main(get_settings())
