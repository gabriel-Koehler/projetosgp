# Acompanhamento das issues — Gabriel Koehler

Última atualização: 2026-10-04. Responsável GitHub: `gabriel-Koehler`.
Fonte: issues atribuídas e PRs de `gabriel-Koehler/projetosgp`.
Este é o arquivo de acompanhamento oficial para atualizar ao concluir cada issue.

## Visão geral
- Total de issues atribuídas: **13**.
- Issues encerradas no GitHub nesta consulta: **8**.
- **8 issues implementadas e integradas na main**, com PRs merged: FE-01, BE-02, FE-02, FE-03, FE-04, FE-05, FE-06 e FE-07.
- FE-04: publicada no PR #56; commit 75327b2.
- FE-05: publicada no PR #57; commit e227db5, derivado de FE-04.
- **5 issues restantes para concluir a implementação**: #3, #22, #23, #25 e #28 (incluindo as parciais do MVP e a infraestrutura a auditar).
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
| [#22 N2-FE-01 — Autenticação e turmas com API real](https://github.com/gabriel-Koehler/projetosgp/issues/22) | Sem entrega específica identificada | Aberta | Cliente usa API mock Python | Integrar e validar API real |
| [#23 N2-FE-02 — Questões e upload com API real](https://github.com/gabriel-Koehler/projetosgp/issues/23) | Sem entrega específica identificada | Aberta | Importação e CRUD usam estado mock | Integrar persistência e upload reais |
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
FE-06 (PR #58, 3f7ce1a) parte da FE-05. FE-07 parte da FE-06 em 3cfa132. Toda a sequência está integrada na main. A próxima issue deve partir da main atualizada, que reúne a última entrega e a documentação existente.

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
