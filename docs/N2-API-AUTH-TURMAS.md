# API persistente para N2-FE-01

Base: main 972a760. Reaproveita as camadas e contratos dos PRs #40, #41 e #42, sem integrar os demais módulos N2 nem alterar o MVP N1.

A fábrica `app.persistent:create_app` fornece login/logout/me, semestres e turmas com PostgreSQL do Supabase. Login consulta `professor` e verifica hash; falta de banco retorna 503, sem aceitar credenciais de demonstração. Cookie N2 separado do N1. O pool abre/fecha com o ciclo de vida da API. Erros de conexão não expõem credenciais.

Configure no `.env` local: DATABASE_URL (connection string PostgreSQL/pooler Supabase com sslmode=require), SECRET_KEY, PROFESSOR_USERNAME, PROFESSOR_PASSWORD e PROFESSOR_NOME. Não versionar esse arquivo. `python -m app.database.migrate` aplica o schema e cria o professor inicial se ausente; execute apenas no banco de desenvolvimento autorizado. `python -m app.database.check` verifica conectividade. Execute `uvicorn app.persistent:create_app --factory --port 8000`.

Os testes de banco precisam de um PostgreSQL descartável em TEST_DATABASE_URL e ALLOW_TEST_DATABASE_RESET=1; eles apagam o schema public e não devem apontar ao Supabase de uso real. Sem essa configuração, ficam explicitamente ignorados.

Pendência de aceite: verificar conexão, migração e persistência no Supabase de desenvolvimento. Nenhuma credencial de banco estava disponível durante a preparação.
