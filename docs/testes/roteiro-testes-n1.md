# Roteiro e Relatório de Testes Navegáveis — N1
 
**Issue:** N1-REQ-02 (#) · **Etapa:** N1 – Passo 04 (Telas Navegáveis com Mock)
**Critério avaliado:** C2 — Sistema Hospedado (link funcionando, telas construídas e navegáveis)
**Responsável:** Eloisa Fazzio da Silva Rocha
 
> ⚠️ Escopo da N1: as telas usam dados estáticos/mock, sem conexão com banco de dados. Este roteiro valida **navegação de ponta a ponta** (toda tela alcançável, sem pontas soltas), não regras de negócio reais — essas entram na N2. Os passos seguem o documento `docs/requisitos/fluxos-de-usuario.md` e o protótipo em Figma.
 
---

## Como usar este documento

Cada caso de teste tem: pré-condição, passos, resultado esperado e uma coluna **Status** (✅ Passou / ❌ Falhou / ⚠️ Bloqueado) preenchida durante a execução no ambiente hospedado. Ao final, o [Resumo da execução](#resumo-da-execução) consolida o resultado geral.

---

## 1. Fluxo do Professor

### CT01 — Login do professor
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Acessar a URL do sistema hospedado | `LoginScreen` é exibida | |
| 2 | Informar credenciais válidas (ou "Continuar com o Google") e confirmar | Usuário é redirecionado ao `DashboardScreen` (Painel) | |

### CT02 — Painel (Dashboard) e atalhos
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | A partir do Painel, conferir estatísticas gerais, gráfico da semana e lista de avaliações recentes | Elementos são exibidos (com dados mock) | |
| 2 | Clicar em "Corrigir prova" | Navega para `CorrecaoScreen` | |
| 3 | Voltar ao Painel e clicar em "Nova avaliação" | Navega para `CriarAvaliacaoScreen` — Passo 1 (Configurar) | |
| 4 | Voltar ao Painel e clicar em "Ver resultados" | Navega para `ResultadosScreen` | |
| 5 | Em qualquer tela do professor, usar o menu lateral fixo | Todos os itens (Painel, Semestres & Turmas, Banco de Questões, Nova Avaliação, Versões & QR Code, Correção Automática, Resultados, Sair da conta) levam à tela correspondente | |

### CT03 — Semestres, Turmas e Alunos
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → menu lateral → "Semestres & Turmas" | Abre `SemestresScreen` com lista de semestres à esquerda | |
| 2 | Selecionar um semestre na lista lateral | Abas "Turmas" e "Alunos" atualizam para o semestre selecionado | |
| 3 | Na aba Turmas, clicar "Nova turma" | Abre formulário de turma | |
| 4 | Preencher e salvar (ou cancelar) o formulário | Retorna à lista de turmas atualizada | |
| 5 | Clicar "Editar" em uma turma existente | Abre formulário preenchido; ao salvar, volta à lista | |
| 6 | Na aba Alunos, clicar "Importar alunos" | Abre fluxo de importação (prévia e confirmação) | |
| 7 | Concluir ou cancelar a importação | Retorna à lista de alunos | |
| 8 | Na lista de semestres, clicar "Editar" em um semestre existente| Botão "Editar" presente em cada card de semestre; abre formulário/modal para alterar os dados |
| 9 | Alterar um campo no formulário de edição e salvar | Lista de semestres atualiza com o novo valor | |
| 10 | Clicar "Excluir" em um semestre **sem** turmas/alunos vinculados (ex.: 2025.1, 0 turmas) | Botão "Excluir" presente; semestre é removido sem erro  |
| 11 | Clicar "Excluir" em um semestre **com** turmas/alunos vinculados (ex.: 2026.1, 5 turmas · 8 alunos) | Sistema avisa/impede a exclusão, ou explica o que acontece com os dados vinculados — não deve apagar silenciosamente | |
| 12 | Clicar "Editar" em um semestre com status "Ativo" e, no formulário, alterar o status para "Encerrado" (ou vice-versa), depois salvar | O card do semestre passa a exibir o novo status (badge "Ativo"/"Encerrado" atualizado) | |
| 13 | Abrir um semestre diferente daquele em que um aluno já está cadastrado e clicar em "Importar alunos" (ou "Novo aluno"), tentando cadastrar o mesmo aluno (mesmo nome/matrícula) nesse outro semestre | Sistema permite o cadastro — matrícula deve ser única por turma/semestre, não bloqueada globalmente | |

### CT04 — Banco de Questões
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → menu lateral → "Banco de Questões" | Abre `BancoQuestoesScreen` com busca, filtro por disciplina e lista de questões | |
| 2 | Clicar "Nova questão" | Abre formulário de questão; ao salvar/cancelar, volta ao banco | |
| 3 | Clicar "Importar" | Abre fluxo de importação Excel/CSV; ao concluir/cancelar, volta ao banco | |
| 4 | Clicar "Editar" em uma questão | Abre formulário preenchido; ao salvar, volta ao banco atualizado | |
| 5 | Clicar "Excluir" em uma questão | Questão é removida da lista exibida; permanece no banco | |

### CT05 — Nova Avaliação (fluxo de 4 passos)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → "Nova avaliação" | Abre `CriarAvaliacaoScreen` — Passo 1 (Configurar), barra de progresso no topo | |
| 2 | Preencher nome, semestre, data, turma, destinatário e clicar "Próxima →" | Avança para Passo 2 (Questões) | |
| 3 | Selecionar questões do banco (painel "Selecionadas" fixo) e clicar "Próxima →" | Avança para Passo 3 (Gabarito) | |
| 4 | Definir a alternativa correta de cada questão e clicar "Próxima →" | Avança para Passo 4 (Versões) | |
| 5 | Definir quantidade de versões, nomes (A/B/C), embaralhar questões/alternativas | Campos refletem a configuração escolhida | |
| 6 | Em qualquer passo, clicar "← Voltar" | Retorna ao passo anterior mantendo os dados preenchidos | |
| 7 | No Passo 1, clicar "← Cancelar" | Retorna ao `DashboardScreen` | |
| 8 | No Passo 4, clicar "Gerar avaliação" | Navega para `VersoesScreen` (Versões e QR Code) | |

### CT06 — Versões, QR Code e documentos
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Em `VersoesScreen`, selecionar uma turma na coluna esquerda | Conteúdo da tela atualiza para a turma selecionada | |
| 2 | Selecionar versão A/B/C nas abas superiores | Questões, gabarito, QR Code e documentos atualizam para a versão | |
| 3 | Abrir aba "Questões" | Lista as questões da versão selecionada | |
| 4 | Abrir aba "Gabarito" | Exibe o gabarito da versão selecionada | |
| 5 | Clicar "Baixar QR (.png)" | Arquivo é baixado; usuário permanece na mesma tela | |
| 6 | Clicar "Baixar tudo (PDF)" | Arquivo é baixado (prova, folha de respostas, gabarito impresso); usuário permanece na mesma tela | |
| 7 | Clicar "Iniciar correção automática" | Navega para `CorrecaoScreen` | |

### CT07 — Correção automática (fluxo feliz)
> Atualizado: no protótipo, a correção acontece em uma única tela (`CorrecaoScreen`), com um passo a passo numerado e um botão único "Iniciar correção" — não em três telas separadas.

| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → "Corrigir prova" (ou via `VersoesScreen`) | Abre `CorrecaoScreen`, mostrando os passos numerados (01 Escanear QR Code, 02 Identificar o aluno, 03 Escanear folha de respostas, 04 Correção automática, 05 Resultado salvo) e a lista "Correções recentes" | |
| 2 | Clicar "Iniciar correção" e simular leitura de um QR Code válido | Versão é identificada e o gabarito é carregado | |
| 3 | Identificar o aluno (buscar por nome ou matrícula) | Aluno é associado à correção em andamento | |
| 4 | Simular leitura confiável da folha de respostas | Sistema compara com o gabarito e calcula a nota | |
| 5 | Verificar o resultado salvo | Resultado aparece na lista "Correções recentes", dentro da própria `CorrecaoScreen` | |
| 6 | A partir da `CorrecaoScreen`, ir para "Resultados" (menu lateral ou atalho) | Navega para `ResultadosScreen` e o novo resultado aparece na lista | |

### CT08 — Correção automática (casos de erro)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Simular QR Code ausente, múltiplo, ilegível ou fora do padrão | Exibe mensagem de erro e permanece na `CorrecaoScreen`, permitindo nova tentativa | |
| 2 | Simular leitura duvidosa da folha de respostas | Exibe mensagem de erro pedindo nova leitura, sem gerar um resultado definitivo | |
| 3 | Tentar avançar sem identificar o aluno | Sistema impede ou sinaliza que o passo "Identificar o aluno" está pendente | |

### CT09 — Resultados e estatísticas
> Atualizado: no protótipo, resultados e estatísticas ficam na mesma tela (`ResultadosScreen`) — não há telas separadas de "Detalhe do resultado" e "Estatísticas".

| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → "Ver resultados" (ou menu lateral) | Abre `ResultadosScreen`, exibindo no topo os cards de estatística (Média da turma, Maior nota, Aprovados, Reprovados) e, abaixo, a tabela de alunos com nota e acertos | |
| 2 | Clicar "Detalhar" em um aluno da tabela | Exibe o detalhe das respostas e da nota daquele aluno (modal ou expansão, a confirmar no protótipo) | |
| 3 | Fechar/voltar do detalhe | Retorna à `ResultadosScreen` sem perder os filtros aplicados | |

### CT10 — Sair da conta
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Em qualquer tela do professor, menu lateral → "Sair da conta" | Usuário é desconectado e redirecionado ao `LoginScreen` | |

---

## 2. Fluxo do Aluno

### CT11 — Consulta do gabarito via QR Code (fluxo feliz)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Escanear o QR Code de uma versão válida com a câmera do celular | Sistema reconhece o QR Code | |
| 2 | Verificar a tela exibida | Abre a "Tela do Gabarito" mostrando **somente** as alternativas corretas da versão | |
| 3 | Conferir que não há login, painel ou menu do professor acessível | Aluno não consegue acessar nenhuma tela administrativa | |

### CT12 — Consulta do gabarito via QR Code (erro)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Escanear um QR Code inválido/inexistente | Sistema exibe mensagem de erro, sem expor gabarito, resposta marcada, nota ou dados administrativos | |

### CT13 — Restrições de acesso do aluno (RN02–RN05)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Tentar acessar diretamente uma URL de tela do professor (Painel, Resultados, Banco de Questões etc.) sem login | Acesso é bloqueado/redirecionado — aluno não possui conta nem visão dessas telas | |
| 2 | Na Tela do Gabarito, conferir que não aparecem: resposta marcada pelo aluno, nota, resultado individual ou estatísticas | Nenhum desses dados é exibido | |

---

## 3. Verificação de integridade da navegação

### CT14 — Nenhuma tela sem entrada ou sem saída
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Percorrer todas as telas listadas na tabela de navegação de `docs/requisitos/fluxos-de-usuario.md` | Toda tela alcançável possui pelo menos uma ação de saída (botão, menu ou "voltar") | |
| 2 | Verificar cada tela (exceto `LoginScreen`) | Toda tela é alcançável a partir de pelo menos uma outra tela ou ação | |
| 3 | Testar navegação pelo botão "Voltar" do navegador em 3 pontos distintos do fluxo | Sistema não quebra nem exibe tela em branco/erro | |

---

## Resumo da execução

| Total de casos | Passou | Falhou | Bloqueado | % de aprovação |
|---|---|---|---|---|
| 16 | `<preencher>` | `<preencher>` | `<preencher>` | `<preencher>` |

**Critério de aceite:** 100% dos testes aprovados no ambiente online.

> Os passos 8 e 9 do CT03 (editar/excluir semestre, RF02) devem Falhar/ficar Bloqueados até que essa funcionalidade seja desenhada no Figma e implementada no código — reportar isso separadamente, não travar a entrega desta issue por uma pendência que não é de documentação/teste.

### Falhas encontradas (se houver)
| ID do caso | Descrição da falha | Severidade | Status da correção |
|---|---|---|---|
**Critério de aceite:** 100% dos testes aprovados no ambiente online.

### Falhas encontradas (se houver)
| ID do caso | Descrição da falha | Severidade | Status da correção |
|---|---|---|---|
