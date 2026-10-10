# Validação Supabase de Diego — 05/10/2026

Projeto: projetosgp (`veyofappfyaoejcjwxky`), organização tusnorhekltyfuyvcsqf, São Paulo. [Painel](https://supabase.com/dashboard/project/veyofappfyaoejcjwxky).

## Executado

- Banco público inicialmente vazio confirmado antes da aplicação.
- `src/database/schema.sql` aplicado duas vezes sem erro: 12 tabelas, todas com RLS.
- `validacao-supabase.sql` executado: seed aplicado duas vezes na mesma transação sem duplicar professor/alunos; constraints de datas e FK rejeitaram entradas inválidas; anon/authenticated não puderam consultar os dados do professor de teste.
- ROLLBACK ao final; consulta confirmou zero professores remanescentes. Nenhum seed de desenvolvimento foi deixado no projeto.
- `storage.sql` executado e bucket `correcoes` confirmado privado; nenhuma policy pública nas tabelas de domínio. Nome do bucket deve ser confirmado pelo backend na integração.
- Oito testes Node e dois testes Python de hospedagem/empacotamento aprovados. Empacotador passou a excluir `.temp` e `.branches` da CLI; caso de regressão cobre esses arquivos.
- Vercel: `/` respondeu HTTP 200; `/health` e `/api/health` HTTP 404. Isto não comprova persistência nem a disponibilidade do backend no site.

## Reproduzir sem senha no comando

Com Supabase CLI autenticada e projeto correto vinculado:

```sh
supabase db query --linked --file src/database/schema.sql
supabase db query --linked --file src/database/validacao-supabase.sql
supabase db query --linked --file src/database/storage.sql
```

Confirmar o projeto antes de executar. O schema destina-se a banco vazio/compatível; não migra bancos anteriores. O teste de seed termina em ROLLBACK; não utilizar reset remoto. Não versionar senha, tokens ou service-role key. Credencial de banco local está em .env.supabase.local, excluída do Git.

## Limites e dependências

A RLS bloqueia o navegador e papéis públicos. Não testa isolamento entre dois professores pelo backend: o servidor deve autorizar cada acesso e sua credencial pode contornar RLS. Bucket privado não comprova upload, URL assinada ou compensação de falha SQL. Não foi criado login de produção nem conectada a Vercel.

Conferência GitHub nesta execução: #40–#45 (backend), #48–#49 (MER/dicionário) e #54 (arquitetura) continuam abertos e sem merge. #61 e #62 também aguardam revisão. Não modificar ou integrar os trabalhos desses colegas sem a revisão estabelecida.

| Entrega de Diego | Estado verificável | Falta |
| --- | --- | --- |
| #31 banco | Projeto provisionado; DDL/RLS/seed transacional validados; bucket privado | Conferir MER/dicionário e integração/papel do backend |
| #33 UML | Modelo e artefatos preparados | Revisão e conciliação com backend integrado |
| #18 pacote N1 | Empacotador e exclusões testados | Validação de Gabriel do conteúdo entregue |
| #17 hospedagem N1 | Configuração e HTTPS do cookie testados | Build Docker/implantação da API e health público |
| #35 hospedagem N2 | Banco preparado | Backend #40–#45 integrado, credenciais no servidor, persistência após reinício |
| #36 pacote N2 | Preparação e pacote revisável | Sistema integrado/homologado e pacote final |

Nenhuma issue encerrada, nenhum merge feito. Publicação deste trabalho em PR dependente da última entrega, com revisão solicitada a Gabriel.

## Integridade local

A pasta original apresentou arquivos 0xFF e um objeto Git corrompido. O trabalho foi executado em clone temporário íntegro das branches publicadas; fontes SQL conferidas antes de aplicação. A recuperação local não altera o histórico remoto.

PR publicado: [#63 — validação real do Supabase e proteção do pacote](https://github.com/gabriel-Koehler/projetosgp/pull/63), commit f7c61f1. Revisão formal solicitada a Gabriel (@gabriel-Koehler). Base: docs/n2-parte1-diagramas-backlog; depende dos PRs #61/#62. Nenhuma issue encerrada e nenhum merge realizado.