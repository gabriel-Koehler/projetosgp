# Acompanhamento das issues — Gabriel Koehler

Última atualização: 2026-10-04. Responsável GitHub: `gabriel-Koehler`.
Fonte: issues atribuídas e PRs de `gabriel-Koehler/projetosgp`.
Este é o arquivo de acompanhamento oficial para atualizar ao concluir cada issue.

## Visão geral
- Total de issues atribuídas: **13**.
- Issues encerradas no GitHub nesta consulta: **0**.
- Entregas já publicadas: FE-01, BE-02, FE-02 e FE-03, com PRs abertos.
- FE-04: implementação e testes concluídos; publicação desta entrega em andamento.
- FE-05: próxima entrega, derivada da FE-04.
- Nenhum PR aberto equivale a merge ou encerramento automático já realizado.

## Controle das entregas

| Issue | Implementação | GitHub | Branch / evidência | Pendência |
| --- | --- | --- | --- | --- |
| [#3 N1-INF-03 — Repositório, labels, templates e Kanban](https://github.com/gabriel-Koehler/projetosgp/issues/3) | Parcial / precisa de auditoria | Aberta | Existem backlog, templates e script de criação de issues | Verificar todos os critérios e quadro Kanban; não foi entregue nesta sequência |
| [#5 N1-FE-01 — Layout e autenticação](https://github.com/gabriel-Koehler/projetosgp/issues/5) | Entregue | Aberta, PR aberto | `feat/n1-fe-01-layout-login`, `3d94c07`; [PR #51](https://github.com/gabriel-Koehler/projetosgp/pull/51) inclui a entrega | Revisão e merge |
| [#6 N1-BE-02 — Mock Python](https://github.com/gabriel-Koehler/projetosgp/issues/6) | Entregue | Aberta, PR aberto | `feat/n1-be-02-python-mock-state`, `dc9e59c` e `b3ae5f3`; [PR #51](https://github.com/gabriel-Koehler/projetosgp/pull/51) | Revisão e merge |
| [#7 N1-FE-02 — Semestres e turmas](https://github.com/gabriel-Koehler/projetosgp/issues/7) | Entregue | Aberta, PR aberto | `feat/n1-fe-02-semestres-turmas`, `be20064`; [PR #52](https://github.com/gabriel-Koehler/projetosgp/pull/52) | Revisão e merge após #51 |
| [#8 N1-FE-03 — Alunos e importação](https://github.com/gabriel-Koehler/projetosgp/issues/8) | Entregue | Aberta, PR aberto | `feat/n1-fe-03-alunos-importacao`, `dc475ef`; [PR #53](https://github.com/gabriel-Koehler/projetosgp/pull/53) | Revisão e merge após #52 |
| [#9 N1-FE-04 — Banco de questões](https://github.com/gabriel-Koehler/projetosgp/issues/9) | Implementada e validada; publicando | Aberta | `feat/n1-fe-04-banco-questoes`, derivada de FE-03 | Commit, push e PR desta entrega |
| [#12 N1-FE-05 — Assistente de avaliações](https://github.com/gabriel-Koehler/projetosgp/issues/12) | Em preparação; MVP parcial existente | Aberta | Próxima branch: `feat/n1-fe-05-criacao-avaliacoes-versoes` | Assistente em 3 etapas, nomes de versões e confirmação interativa |
| [#13 N1-FE-06 — Impressão e tela aluno](https://github.com/gabriel-Koehler/projetosgp/issues/13) | Parcial no MVP; issue não concluída | Aberta | Há consulta de versões e QR no MVP | Executar os critérios de impressão de provas, folha de respostas e tela aluno |
| [#14 N1-FE-07 — Correção e estatísticas simuladas](https://github.com/gabriel-Koehler/projetosgp/issues/14) | Parcial no MVP; issue não concluída | Aberta | Há respostas manuais, notas, gráfico e CSV | Validar e completar o fluxo específico da issue |
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

