# Publicação integrada na Vercel

## Arquitetura

`vercel.json` declara dois serviços no mesmo projeto: `web` (Express/EJS) e `python` (FastAPI, `app.vercel:app`). As rotas `/api/*` chegam diretamente ao Python. O Node consulta a sessão por um binding interno `PYTHON_API_URL`, sem depender de localhost nem de uma URL fixa de produção. O banco PostgreSQL é externo, no Supabase; o mock em memória não participa deste deploy.

Referências: [Services](https://vercel.com/docs/services), [bindings](https://vercel.com/docs/services/bindings). Services está em beta. A validação local não substitui a compilação e o teste no projeto da Vercel.

## Variáveis no projeto da Vercel

Configure em Settings → Environment Variables, para os ambientes desejados:

| Nome | Valor |
| --- | --- |
| `DATABASE_URL` | URI PostgreSQL do Supabase, preferencialmente pooler transaction (6543), com `sslmode=require`. Codifique caracteres especiais da senha na URI. |
| `SECRET_KEY` | Chave aleatória fixa e longa. Gere localmente com `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `SESSION_HTTPS_ONLY` | `true` |
| `DATA_MODE` | `real` |
| `PUBLIC_BASE_URL` | URL pública do frontend, por exemplo `https://projetosgp-e9dz.vercel.app`. |
| `SUPABASE_URL` | Opcional: URL HTTPS do projeto para Storage. |
| `SUPABASE_KEY` | Opcional: service_role, somente no servidor, para salvar fotos de correções automáticas. |
| `SUPABASE_BUCKET` | `folhas-resposta`, bucket privado, se usar Storage. |

Não cadastre `PYTHON_API_URL`: a Vercel a injeta no serviço web. Remova o antigo `API_TARGET=http://127.0.0.1:8000`; fora de Services, `API_TARGET` deve ser a origem de uma API publicada. Nunca use a URL HTTPS do projeto Supabase como `DATABASE_URL`.

Em Preview use um banco separado de produção e ajuste `PUBLIC_BASE_URL` ao domínio de teste. Não reutilize um banco real nos testes automatizados que apagam dados.

## Preparação do banco e do acesso

Em um ambiente local com as dependências instaladas, configure as mesmas `DATABASE_URL` e `SECRET_KEY` e escolha `PROFESSOR_USERNAME`, `PROFESSOR_PASSWORD` e `PROFESSOR_NOME` no `.env`. Então execute:

```sh
python -m app.database.migrate
```

O script aplica `app/database/schema.sql` e cria o professor se o username ainda não existir. Não troca a senha de um professor existente. As variáveis `PROFESSOR_*` não fazem login direto na API de produção e não criam o usuário apenas por iniciar o servidor. A migração não é executada automaticamente no build ou em cada requisição.

## Deploy e verificação

1. Publique a branch integrada e selecione-a no projeto; depois do merge, mantenha `main` como Production Branch.
2. Mantenha Root Directory na raiz do repositório. A configuração de serviços define os frameworks; remova overrides antigos de build/output que contradigam `vercel.json`.
3. Faça novo deploy após configurar variáveis. Confira os logs de build de ambos os serviços, incluindo as dependências nativas do OpenCV.
4. Acesse `/api/health`: deve responder 200 e `{"status":"ok","banco":"ok"}`. `/health` verifica também a comunicação do Node com a API.
5. Abra `/`, autentique com o professor criado na migração, crie uma turma e avaliação. Imprima a folha de respostas do backend e teste correção manual, leitura de imagem, resultados e Excel.
6. Libere um gabarito e abra o link de aluno em janela sem login; ao revogar, ele deve ficar indisponível.

Uploads na tela de leitura ficam limitados a 4 MB (PNG/JPEG), deixando margem para o corpo multipart. PDFs são gerados para impressão, não aceitos pelo leitor óptico. A revisão de respostas grava pela rota manual; essa operação não salva a foto no Storage. A rota automática `/api/correcoes` mantém o suporte à foto opcional no Storage.

## Diagnóstico

- Health com `nao_configurado`: conferir `DATABASE_URL` no serviço Python.
- Health com `indisponivel`: conferir conexão, senha, pooler e disponibilidade do Supabase.
- Login 401: conferir o usuário criado pela migração; não usar a senha do banco.
- Página de indisponibilidade com API saudável: conferir binding e logs do serviço web.
- Cookie não persiste: conferir `SECRET_KEY` fixa, HTTPS e domínio.

Sem acesso ao projeto Vercel e às credenciais Supabase, só é possível validar código e ambiente local. Um PR aberto ainda não altera a publicação da `main`.
