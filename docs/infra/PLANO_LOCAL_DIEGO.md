# Plano de entregas locais de Diego — 05/10/2026

Base Git: 972a760; branch infra/diego-entregas-locais. As seis issues #17/#18/#31/#33/#35/#36 permanecem abertas. Nenhum push, PR, deploy ou provisionamento foi realizado. Revisão por Gabriel conforme AGENTS.md. A branch única organiza a preparação local; o fluxo formal das issues será aplicado quando autorizado.

| Card | Artefatos locais | Pendência |
| --- | --- | --- |
| N1-INF-01 | Dockerfile, render.yaml, inicializador, /health, cookie HTTPS | Build e publicação HTTPS |
| N1-INF-02 | Empacotador e ZIP | Revisão / entrega formal |
| N2-INF-01 | .env.example, schema, seed e DER | Executar PostgreSQL e provisionar Supabase |
| N2-INF-02 | UML conforme modelos do PR #45 | Reconferir após integração N2 |
| N2-INF-03 | Plano de produção | Integração sem mocks e deploy real |
| N2-INF-04 | ZIP de preparação e roteiro | Homologação N2 final |

## Execução local

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm.cmd ci
npm.cmd run dev:all
```

Frontend em http://127.0.0.1:3000 e FastAPI em http://127.0.0.1:8000. Node 24 carrega o .env pelo inicializador; processos avulsos recebem variáveis explicitamente. A .venv local precisa de instalação completa antes de uso; nesta sessão as dependências foram validadas em pasta temporária.

O MVP /api usa memória; o backend modular permanece em /n1. Variáveis PROFESSOR_* pertencem ao backend modular, enquanto o login do MVP usa MemoryProvider. Google e recuperação são simulações N1.

## Hospedagem N1

Uma imagem Docker contém Node e Python, com API em loopback, proxy público e apenas um worker (mocks/sessões em memória). /health depende da API. O inicializador encerra os processos se um falhar.

```powershell
docker build -t avaliasystem-n1 .
docker run --rm -p 3000:3000 --env-file .env avaliasystem-n1
```

SECRET_KEY deve permanecer fora do Git. SESSION_HTTPS_ONLY=false para HTTP local e true para HTTPS. PUBLIC_BASE_URL recebe a URL pública quando existir. Render blueprint segue a [referência oficial](https://render.com/docs/blueprint-spec); deploy automático está desativado nesta preparação. Build Docker não executado: ferramenta ausente. A validação pública futura deve cobrir saúde, sessão/login, CRUD, impressão e consulta de gabarito.

## Supabase / N2

Schema baseado no PR #45, commit fdb310dac8de60ad10712b79f6fc415aeabe22f2, compatível com repositories do Luan: português/BIGSERIAL. O schema anterior inglês/UUID foi preservado em deliveries/local-backup. Nenhum PR N2 foi mesclado.

Em PostgreSQL vazio, usar psql -v ON_ERROR_STOP=1 -f src/database/schema.sql, depois seed.sql; repetir e verificar duplicatas. IF NOT EXISTS não migra tabelas existentes. Seed apenas acadêmico, sem login válido.

RLS habilitada sem policies públicas, conforme [documentação Supabase](https://supabase.com/docs/guides/database/postgres/row-level-security). Usar papel PostgreSQL do servidor com acesso adequado e autorização por professor nos services/repositories. DATABASE_URL e SUPABASE_SERVICE_ROLE_KEY não devem chegar ao navegador. A main N1 ignora as variáveis de banco: configurar ambiente não converte mocks em persistência.

Integrar backend e frontend N2 antes de ajustar o entrypoint de produção. Configurar DATABASE_URL, SUPABASE_URL e chave de servidor no provedor. Provisionamento, aplicação SQL e conectividade não executados.

Homologação N2: criar professor/turmas; importar alunos/questões; gerar versões; reiniciar e conferir persistência; testar isolamento entre professores; corrigir OMR; validar notas e Excel; liberar/revogar gabarito; conferir HTTPS e sessão. Só depois emitir entrega final e registrar URL real.

## Pacotes e auditoria

```powershell
python scripts/package_delivery.py --output deliveries/projetosgp-n1-local.zip
python scripts/package_delivery.py --output deliveries/projetosgp-n2-preparacao-local.zip
python -m unittest discover -s tests -p test_delivery_package.py
```

Os ZIPs representam o workspace local atual; o segundo é preparação N2, não produto N2 homologado. Excluem Git, node_modules, venvs, caches, segredos, backups e ZIPs anteriores; preservam .env.example. A auditoria de 05/10/2026 encontrou dez PRs N2 abertos; não declarar zero PRs abertos. Não alterar revisores antigos do backlog em lugar da instrução atual de Gabriel.

Consultar [diário](../DIARIO_DE_BORDO_DIEGO.md), [validação](VALIDACAO_LOCAL.md), [DER](../arquitetura/der-fisico-n2.md), [UML](../arquitetura/diagrama-classes-uml-v2.md) e [Figma](REVISAO_FIGMA.md).
