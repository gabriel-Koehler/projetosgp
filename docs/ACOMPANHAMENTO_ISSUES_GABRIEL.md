# Acompanhamento das issues — Gabriel Koehler

Última atualização: 2026-10-07. Responsável GitHub: `gabriel-Koehler`.
Fonte: issues atribuídas e PRs de `gabriel-Koehler/projetosgp`.
Este é o arquivo de acompanhamento oficial para atualizar ao concluir cada issue.

## Visão geral
- Total de issues atribuídas: **13**.
- Issues encerradas no GitHub nesta consulta: **8**.
- **8 issues implementadas e integradas na main**, com PRs merged: FE-01, BE-02, FE-02, FE-03, FE-04, FE-05, FE-06 e FE-07.
- FE-04: publicada no PR #56; commit 75327b2.
- FE-05: publicada no PR #57; commit e227db5, derivado de FE-04.
- **3 issues sem implementação final**: #3, #25 e #28. As #22 e #23 estão implementadas e validadas com PostgreSQL local; falta homologar no Supabase e revisar/integrar os PRs. A #23 também aguarda validação visual em navegador.
- Merges confirmados no GitHub: PRs #51, #52, #53, #56, #57, #58 e #59. Issues #5, #6, #7, #8, #9, #12, #13 e #14 encerradas.

## Controle das entregas

| Issue | Implementação | GitHub | Branch / evidência | Pendência |
| --- | --- | --- | --- | --- |
| [#3 N1-INF-03 — Repositório, labels, templates e Kanban](https://github.com/gabriel-Koehler/projetosgp/issues/3) | Parcial / precisa de auditoria | Aberta | Existem backlog, templates e script de criação de issues | Verificar todos os critérios e quadro Kanban; não foi entregue nesta sequência |
| [#5 N1-FE-01 — Layout e autenticação](https://github.com/gabriel-Koehler/projetosgp/issues/5) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-01-layout-login`, `3d94c07`; [PR #51](https://github.com/gabriel-Koehler/projetosgp/pull/51) inclui a entrega | Nenhuma pendência de integração |
| [#6 N1-BE-02 — Mock Python](https://github.com/gabriel-Koehler/projetosgp/issues/6) | Integrada na main | Encerrada, PR merged | `feat/n1-be-02-python-mock-state`, `dc9e59c` e `b3ae5f3`; [PR #51](https://github.com/gabriel-Koehler/projetosgp/pull/51) | Nenhuma pendência de integração |
| [#7 N1-FE-02 — Semestres e turmas](https://github.com/gabriel-Koehler/projetosgp/issues/7) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-02-semestres-turmas`, `be20064`; [PR #52](https://github.com/gabriel-Koehler/projetosgp/pull/52) | Nenhuma pendência de integração |
| [#8 N1-FE-03 — Alunos e importação](https://github.com/gabriel-Koehler/projetosgp/issues/8) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-03-alunos-importacao`, `dc475ef`; [PR #53](https://github.com/gabriel-Koehler/projetosgp/pull/53) | Nenhuma pendência de integração |
| [#9 N1-FE-04 — Banco de questões](https://github.com/gabriel-Koehler/projetosgp/issues/9) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-04-banco-questoes`, `75327b2`; [PR #56](https://github.com/gabriel-Koehler/projetosgp/pull/56) | Nenhuma pendência de integração |
| [#12 N1-FE-05 — Assistente de avaliações](https://github.com/gabriel-Koehler/projetosgp/issues/12) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-05-criacao-avaliacoes-versoes`, `e227db5`; [PR #57](https://github.com/gabriel-Koehler/projetosgp/pull/57) | Nenhuma pendência de integração |
| [#13 N1-FE-06 — Impressão e tela aluno](https://github.com/gabriel-Koehler/projetosgp/issues/13) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-06-impressao-prova-aluno`, `3f7ce1a`; [PR #58](https://github.com/gabriel-Koehler/projetosgp/pull/58) | Nenhuma pendência de integração |
| [#14 N1-FE-07 — Correção e estatísticas simuladas](https://github.com/gabriel-Koehler/projetosgp/issues/14) | Integrada na main | Encerrada, PR merged | `feat/n1-fe-07-correcao-estatisticas`, `3c2d899`; [PR #59](https://github.com/gabriel-Koehler/projetosgp/pull/59) | Nenhuma pendência de integração |
| [#22 N2-FE-01 — Autenticação e turmas com API real](https://github.com/gabriel-Koehler/projetosgp/issues/22) | Implementada; PostgreSQL local validado | Aberta, [PR #64](https://github.com/gabriel-Koehler/projetosgp/pull/64) | `feat/n2-fe-01-integracao-auth-turmas`, `5fd72c1`, base `feat/n2-api-auth-turmas` ([PR #60](https://github.com/gabriel-Koehler/projetosgp/pull/60)) | Validar no Supabase de desenvolvimento; revisão e merge |
| [#23 N2-FE-02 — Questões e upload com API real](https://github.com/gabriel-Koehler/projetosgp/issues/23) | Implementada; PostgreSQL local revalidado em 2026-10-07 | Aberta, [PR #65](https://github.com/gabriel-Koehler/projetosgp/pull/65) aberto | `feat/n2-fe-02-integracao-questoes-upload`, `6ab665a`, base da #22 em `121fbdb` | Supabase remoto, navegador desktop/mobile, revisão e merge |
| [#25 N2-FE-03 — Avaliações e versões persistidas](https://github.com/gabriel-Koehler/projetosgp/issues/25) | Sem entrega específica identificada | Aberta | Avaliações ainda em memória | Integrar criação e persistência reais |
| [#28 N2-FE-04 — Correção real e Excel](https://github.com/gabriel-Koehler/projetosgp/issues/28) | Sem entrega específica identificada | Aberta | Correção manual simulada e CSV | Integrar correção real e relatório XLSX |

## Como atualizar a cada issue
- [ ] Consultar a issue e registrar critérios de aceite.
- [ ] Criar branch a partir da última entrega, anotando a base.
- [ ] Implementar e validar fluxos, erros e layout mobile.
- [ ] Atualizar a linha da issue e evidências abaixo.
- [ ] Fazer commit e push; registrar PR e revisor.
- [ ] Após revisão, verificar separadamente merge do PR e encerramento da issue.
- [ ] Atualizar data, totais e próxima issue.
- [ ] Manter dependências dos PRs explícitas; não marcar futuros trabalhos como concluídos.

## Registro para próximas entregas
Copiar este bloco ao iniciar uma issue:

### [ID] — Título
- Issue:
- Branch base:
- Branch de trabalho:
- Status de implementação:
- Critérios atendidos:
- Testes e evidências:
- Commit(s):
- Pull request / revisor:
- Status de merge:
- Pendências:
- Data da atualização:

## Evidências atuais
- FE-04: CRUD, filtros por disciplina/dificuldade/texto, alternativas recolhíveis e gabarito visível.
- Importação de questões CSV com modelo, prévia, validação de linhas e proteção contra duplicados; lote atômico.
- 9 testes Python e testes CSV de questões/alunos aprovados.
- Fluxo FE-04 aprovado em navegador: inclusão, edição, filtros, recolhimento, importação, exclusão e mobile.


## Revisores das issues
Em 2026-10-04, atualizado o campo Revisor de 32 issues para Gabriel Koehler da Silva (@gabriel-Koehler). As descrições das quatro issues atribuídas à Eloisa (#2, #15, #29, #30) foram preservadas e comparadas após a edição. Isso registra a alteração nas descrições das issues, não a realização de code review ou merge.

## Evidências FE-05
Assistente de 3 etapas, nomes únicos, rascunho por usuário, contadores, confirmação por cards, gabaritos e QR de nomes personalizados. 10 testes Python aprovados e fluxo desktop/mobile validado.

## Sequência de branches e PRs
FE-03 (PR #53) → FE-04 (PR #56, 75327b2) → FE-05 (PR #57, e227db5).
FE-06 (PR #58, 3f7ce1a) parte da FE-05. FE-07 parte da FE-06 em 3cfa132. Toda a sequência está integrada na main. Registro histórico da integração N1. A sequência N2 agora é `feat/n2-api-auth-turmas` (PR #60) → `feat/n2-fe-01-integracao-auth-turmas` (PR #64) → `feat/n2-fe-02-integracao-questoes-upload` (#23). Novas entregas devem preservar a branch mais atual desta sequência.

## Evidências FE-06
Impressão A4 de prova, folha com QR/bolhas A–D e gabarito do professor. Liberação explícita e revogável do gabarito público, com página do aluno responsiva. 11 testes Python aprovados. Navegador: prova de 45 questões, PDFs de 10/2/5 páginas, revisão visual e acesso anônimo/revogação em 390 px. Dados permanecem em memória.


## Evidências FE-07
- Upload local de PNG/JPEG/PDF com validação de formato e limite de 10 MB; feedback por etapas e prévia de imagem.
- Leitura explicitamente simulada, respostas editáveis, confirmação obrigatória, entrada manual e proteção contra duplicidade.
- Notas por aluno, conferência de respostas, filtros de avaliação/aluno, relatório imprimível e CSV do filtro.
- Percentual de acertos e alternativas mais marcadas, com empates e identificação original preservada entre versões embaralhadas.
- 12 testes Python e 8 testes Node aprovados. Navegador: upload, revisão, notas 10/0, estatística 50%, filtros, CSV, estado vazio, duplicidade e viewport 390 px sem overflow.
- Dados permanecem em memória e não há OCR real. PR integrado e issue encerrada após a autorização de merge do responsável.


## Integração na main — 2026-10-04
- Autorização: reunir todas as features desta sequência na main.
- Integração sequencial com merge commits, preservando o histórico e a documentação já existente na main.
- Último merge de funcionalidades: 3407672 (PR #59).
- Árvore da main comparada com a integração local validada: nenhuma diferença.
- Validação do conjunto: 12 testes Python e 8 testes Node aprovados.
- Permanecem pendentes a auditoria N1-INF-03 (#3) e as quatro integrações N2 (#22, #23, #25 e #28).

## Demais PRs N1 integrados — 2026-10-04
- PR #37: setup da API Python e autenticação modular.
- PR #38: embaralhamento e gabaritos próprios por versão.
- PR #39: QR Code e consulta pública restrita do gabarito.
- PR #47: roteiro e relatório de testes de aceitação.
- PR #50: histórico dos fluxos e casos de uso (sem alteração líquida de arquivos nesta integração).
- PR #55: classes de domínio.
- Todos os seis PRs estão merged na main. Consulta final: nenhum PR N1 aberto; nove PRs N2 continuam abertos.
- Conflitos de contratos de API resolvidos mantendo /api do MVP e disponibilizando o backend modular em /n1 na porta 8000; detalhes em INTEGRACAO_N1.md.
- Validação: 116 testes Python e 8 testes JavaScript aprovados, incluindo isolamento de sessões, links QR sob /n1 e consulta pública.
- O merge desses PRs não conclui a auditoria da issue #3 nem implementa as integrações N2 pendentes.

## Entrega N2-FE-01 — 2026-10-05
- API requerida localizada nos PRs #40–42, ainda não integrados. Dependência adaptada na branch feat/n2-api-auth-turmas, PR #60, baseada na main 972a760.
- Frontend desenvolvido em seguida, na branch feat/n2-fe-01-integracao-auth-turmas, preservando o MVP N1 e conectando login/semestres/turmas à API persistente.
- 145 testes Python aprovados com PostgreSQL local real; 11 testes JavaScript e fluxo de navegador desktop/mobile aprovados. Persistência após reiniciar API/pool confirmada.
- Sem .env Supabase fornecido; aceite nesse ambiente externo permanece pendente. Issue #22 aberta, nenhum merge realizado nesta entrega.


## Entrega N2-FE-02 — 2026-10-06
- Issue: #23; iniciada por instrução do responsável, mantendo explícitas as pendências de aceite da #22.
- Branch base: `feat/n2-fe-01-integracao-auth-turmas`, atualizada via fetch em `121fbdb`.
- Branch de trabalho: `feat/n2-fe-02-integracao-questoes-upload`.
- Implementação: CRUD persistente de questões, carregamento completo paginado, categoria e alternativa E, upload multipart CSV/XLSX, modelos autenticados, prévia sem gravação e confirmação transacional com revalidação no banco. Endpoints reaproveitados do PR #42 e adaptados à API desta sequência.
- Validação: 183 testes Python aprovados em PostgreSQL 16.14 local descartável, incluindo isolamento, persistência após recriar API/pool, duplicadas entre prévia/confirmação e rollback; 13 testes JavaScript aprovados; diff e sintaxe verificados.
- Commit de implementação: `6ab665a`. Push ao origin recusado com HTTP 403: única conta configurada `tnah-Gabriel-Silva`, sem permissão de escrita. Nenhum PR criado. Publicação aguarda conta com acesso ou autorização para fork; o PR deve apontar à branch da #22 e declarar dependência dos PRs #64 e #60 e reaproveitamento do #42.
- Revisor: Gabriel Koehler da Silva (@gabriel-Koehler).
- Status: implementação entregue localmente; sem merge, issue aberta.
- Pendências: configuração e homologação em Supabase de desenvolvimento; navegador desktop/mobile indisponível na sessão; revisão e merge mediante autorização. Não iniciar #25 nesta entrega.
- Detalhes: docs/N2-FE-02.md.
- Fluxo HTTP pelo proxy Express validado com API e banco locais: login/cookie, painel/config, CRUD, modelos CSV/XLSX, multipart, prévia/confirmação, duplicadas e logout. Nenhuma migração remota executada.

## Regularização N2-FE-02 — 2026-10-07
- Bloqueio de publicação resolvido com a conta já configurada `gabriel-Koehler`; push confirmado para a branch da #23.
- [PR #65](https://github.com/gabriel-Koehler/projetosgp/pull/65) aberto para `feat/n2-fe-01-integracao-auth-turmas`. Dependências #64 e #60, reaproveitamento #42 e pendências de aceite explícitos na descrição.
- Revisor indicado: @gabriel-Koehler. GitHub não permite solicitar revisão ao próprio autor; indicação preservada na descrição.
- Revalidação: 183 testes Python e 13 testes JavaScript aprovados. Fluxo HTTP pelo proxy Express novamente aprovado em banco PostgreSQL local separado.
- API GitHub confirmou PR #65 e issue #23 abertos; nenhum merge ou encerramento realizado.
- Pendências externas: configurar e autorizar Supabase de desenvolvimento para homologação; disponibilizar navegador conectado para validação visual desktop/mobile. Não há `.env` nem `DATABASE_URL` nesta sessão; inventário de navegadores vazio e navegador integrado indisponível.
- Próxima implementação na sequência: #25, após concluir o aceite da #23. Branch futura `feat/n2-fe-03-integracao-avaliacoes-versoes`, partindo da versão mais atual da branch da #23. Nenhuma branch da #25 criada.
- Dependência de Diego consultada no GitHub: issue #31, branch `infra/diego-validacao-supabase` em `f8f16e0`, [PR #63](https://github.com/gabriel-Koehler/projetosgp/pull/63), dependente de #61/#62; PR e issue abertos, sem merge. A documentação dessa branch registra o projeto Supabase `projetosgp` (`veyofappfyaoejcjwxky`) já provisionado e DDL/RLS/seed validados remotamente. Não é necessário criar outro projeto.
- Compatibilidade conferida: mesmas tabelas/colunas/índices da API, acrescidos de transação e RLS. DDL de Diego aplicado em banco local separado, com 12 tabelas e RLS em todas; fluxo HTTP da #23 aprovado sobre esse schema. Isso não substitui a validação das permissões/conexão do backend remoto.
- A conexão de Diego está documentada como `.env.supabase.local` não versionado; arquivo indisponível neste workspace. Pendência corrigida: obter acesso ao projeto já provisionado e homologar o fluxo da #23, sem repetir o provisionamento. Detalhes em `docs/N2-FE-02.md`.
