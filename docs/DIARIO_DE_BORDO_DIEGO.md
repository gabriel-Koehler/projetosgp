# Diário de bordo — Diego Rafael da Silva Dornelles

**Data:** 05/10/2026, America/Sao_Paulo. **Projeto:** projetosgp / AvaliaSystem. **Área:** infraestrutura, deploy, entrega e modelagem física. Execução local assistida pelo Codex a pedido de Diego; não representa publicação ou aprovação formal.

## Atividades realizadas

1. Conferido o Git: main em abe0062, 45 commits atrás da referência. Executado fetch e fast-forward até 972a760; criada branch local infra/diego-entregas-locais.
2. Preservados artefatos locais anteriores em deliveries/local-backup: ambiente exemplo, schema e seed. A criação original desses arquivos não é atribuída a esta sessão.
3. Consultado o GitHub público: confirmadas seis issues de Diego (#17, #18, #31, #33, #35, #36); dez PRs N2 abertos. Auditoria salva em docs/infra/github-audit-2026-10-05.json. Nenhuma alteração remota.
4. Preparados Dockerfile, .dockerignore, render.yaml e inicializador Node/Python. Ajustado HOST do frontend, criado /health e configurado cookie seguro por SESSION_HTTPS_ONLY. Criado .env local com chave aleatória, sem credenciais Supabase, e carregamento pelo inicializador local.
5. Revisado empacotador: exclui Git, ambientes, node_modules, caches, segredos, backups e ZIPs anteriores; evita incluir o próprio arquivo. Criado teste de geração repetida, exclusões e extração.
6. Compatibilizados schema/seed e DER com contrato português/BIGSERIAL do Luan, PR #45, commit fdb310dac8de60ad10712b79f6fc415aeabe22f2. O modelo inicial inglês/UUID foi preservado. RLS habilitada sem policies públicas; autorização permanece responsabilidade do backend.
7. Elaborado UML v2 com atributos dos modelos reais do PR N2 consultado, diferenciando referência futura e core N1 local.
8. Documentados execução, hospedagem futura, configuração Supabase e roteiro de homologação em docs/infra/PLANO_LOCAL_DIEGO.md.
9. Conferido Figma: HTTP 200 e miniatura de login inspecionada, coerente com login.ejs. Demais telas não acessadas; conformidade completa pendente. Ver docs/infra/REVISAO_FIGMA.md.
10. Validados oito testes Node e 118 testes Python (4,90 s), incluindo empacotador/cookie HTTPS. Frontend testado com login e health 200/503. Dependências validadas em ambiente temporário; instalação da .venv local pendente.
11. Repetição final da suite: 117 aprovados e uma falha de leitura QR; o caso isolado passou em 1,55 s. Registrada pendência de estabilidade antes da homologação.
12. Detectados erros de gravação no workspace durante conferência final; reconstruídos artefatos em pasta temporária para cópia e nova verificação. Dependências previamente versionadas foram recuperadas a partir de HEAD. npm informou quatro vulnerabilidades nas dependências atuais; revisão pendente.

## Situação dos cards

| Card / issue | Entrega local | Pendência formal |
| --- | --- | --- |
| N1-INF-01 / #17 | Docker / Render / inicializador / saúde / HTTPS | Build Docker, publicação e URL HTTPS |
| N1-INF-02 / #18 | Empacotador, teste e ZIP local | Revisão e fechamento; auditoria não declara zero PRs |
| N2-INF-01 / #31 | SQL, seed, DER e variáveis exemplo | Execução SQL e provisionamento Supabase |
| N2-INF-02 / #33 | UML conforme referência N2 | Reconferir após integração; revisão |
| N2-INF-03 / #35 | Plano de produção e configuração | N2 integrada sem mocks, segredos e deploy |
| N2-INF-04 / #36 | Pacote de preparação e roteiro | Homologação final N2 |

## Evidências e próximos passos

[Validação local](infra/VALIDACAO_LOCAL.md), [plano local](infra/PLANO_LOCAL_DIEGO.md), [DER](arquitetura/der-fisico-n2.md), [UML](arquitetura/diagrama-classes-uml-v2.md) e [Figma](infra/REVISAO_FIGMA.md).

Docker e PostgreSQL não estão disponíveis: build, DDL/seed e conectividade real não foram executados. Integrar dependências N2 pelo fluxo do projeto, revisar integridade e isolamento, testar Docker, publicar quando autorizado, homologar HTTPS/persistência/OMR/Excel e emitir pacote final. Gabriel é o revisor atual das entregas de Diego conforme AGENTS.md.

As seis issues seguem abertas. Nenhum push, PR, encerramento, merge remoto, deploy ou provisionamento Supabase foi realizado. Tudo permanece local.

## N2 – Parte 1: diagramas e backlog — 05/10/2026

Atendendo à solicitação local, foram preparados quatro diagramas do AvaliaSystem: caso de uso, atividade, classe e sequência. Cada documento apresenta o passo a passo, duas imagens intermediárias e uma final, além das fontes PlantUML. Os modelos representam o projeto N2 proposto e exigem revisão do grupo; não demonstram implementação ou homologação das funcionalidades.

Foi montada a planilha Excel com 45 tarefas específicas, critérios de aceite, responsáveis, esforço, predecessoras e datas por tarefa. Cada integrante recebeu nove tarefas: Gabriel e Luan com 38 horas; Alyson, Eloisa e Diego com 36 horas cada. Total estimado: 184 horas. Todas estão planejadas para validação, sem atribuir conclusão aos demais integrantes.

Cronograma provisório: 05/10 a 13/11/2026, até quatro horas por pessoa/dia útil. A data oficial da N2 e o arquivo “Exemplo Atividade.md” da aula ainda precisam ser confirmados. Conferência completa do Figma permanece pendente conforme o relatório anterior.

Validação desta entrega: integridade ZIP/XML do XLSX, abertura das cinco abas, caches de fórmulas/dependências, 45 tarefas, equilíbrio de horas e datas compatíveis com predecessoras/capacidade. Doze SVG tiveram XML validado; as quatro imagens finais foram renderizadas localmente para inspeção visual. O motor PlantUML não foi executado. Não foi necessário repetir testes do aplicativo, pois esta etapa acrescenta documentação e planilha.

Artefatos: [índice N2 Parte 1](n2-parte1/README.md) e [planilha Excel](n2-parte1/backlog/planejamento-backlog-n2.xlsx). Branch local docs/n2-parte1-diagramas-backlog. Sem commit, push, PR, deploy ou alteração remota nesta etapa.
## Commits locais para revisão de Gabriel — 05/10/2026

Por solicitação do usuário, as entregas foram registradas em commits locais na branch docs/n2-parte1-diagramas-backlog: 345c7e5 (hospedagem), e1aa3cb (empacotamento), efc7353 (banco/DER/UML) e 32ca0e5 (diagramas/backlog). Revisor indicado: Gabriel Koehler da Silva (@gabriel-Koehler); análise e validação ainda pendentes. O commit documental seguinte reúne evidências e roteiro de revisão. Os registros “sem commit” acima são históricos.

Validação antes dos commits: 8 testes Node e 2 testes Python específicos aprovados; diff sem erros de whitespace. Limitações anteriores mantidas, incluindo QR intermitente, ausência de build Docker/execução PostgreSQL e prazo acadêmico provisório. [Roteiro de revisão](infra/REVISAO_GABRIEL.md). Nenhum push, PR, merge ou encerramento de issue foi realizado.
## Publicação autorizada para revisão de Gabriel

Após autorização explícita do usuário, as branches e os cinco commits de Diego foram enviados ao GitHub. PRs abertos, ambos com revisão formal solicitada a @gabriel-Koehler:

- [PR #61 — infraestrutura, empacotamento e banco/UML](https://github.com/gabriel-Koehler/projetosgp/pull/61): infra/diego-entregas-locais → main; commits 345c7e5, e1aa3cb e efc7353.
- [PR #62 — diagramas, backlog e evidências](https://github.com/gabriel-Koehler/projetosgp/pull/62): docs/n2-parte1-diagramas-backlog → infra/diego-entregas-locais; commits 32ca0e5 e d8e99e3. Depende do PR #61.

Os registros anteriores de ausência de push/PR são históricos. Análise e validação de Gabriel pendentes; nenhuma issue encerrada, merge ou deploy realizado. Este registro é enviado como commit adicional ao PR #62.