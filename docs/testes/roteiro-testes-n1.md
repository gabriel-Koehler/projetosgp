# Roteiro e Relatório de Testes Navegáveis — N1

**Issue:** N1-REQ-02 (#) · **Etapa:** N1 – Passo 04 (Telas Navegáveis com Mock)
**Critério avaliado:** C2 — Sistema Hospedado (link funcionando, telas construídas e navegáveis)
**Responsável:** Eloisa Fazzio da Silva Rocha
**Ambiente testado:** `<URL do sistema hospedado>`
**Data da execução:** `<preencher>`
**Navegador/dispositivo:** `<preencher>`

> ⚠️ Escopo da N1: as telas usam dados estáticos/mock, sem conexão com banco de dados. Este roteiro valida **navegação de ponta a ponta** (toda tela alcançável, sem pontas soltas), não regras de negócio reais — essas entram na N2. Os passos seguem o documento `docs/requisitos/fluxos-de-usuario.md`.

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
| 2 | Clicar em "Corrigir prova" | Navega para a tela de Escanear QR Code (correção) | |
| 3 | Voltar ao Painel e clicar em "Nova avaliação" | Navega para `CriarAvaliacaoScreen` — Passo 1 (Configurar) | |
| 4 | Voltar ao Painel e clicar em "Ver resultados" | Navega para a tela Resultados | |
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
| 7 | Clicar "Iniciar correção automática" | Navega para a tela de Escanear QR Code (correção) | |

### CT07 — Correção automática (fluxo feliz)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → "Corrigir prova" (ou via `VersoesScreen`) | Abre tela "Escanear QR Code" | |
| 2 | Simular leitura de um QR Code válido | Versão é identificada, gabarito carregado; avança para "Escanear Folha de Respostas" | |
| 3 | Simular leitura confiável da folha de respostas | Sistema compara com o gabarito, calcula a nota e salva o resultado | |
| 4 | Ao concluir, verificar a tela "Resultado da Correção" | Resultado salvo é exibido | |
| 5 | Clicar "Corrigir outra folha" | Retorna à tela "Escanear QR Code" | |
| 6 | Voltar ao "Resultado da Correção" e clicar "Ver resultados" | Navega para a tela Resultados | |

### CT08 — Correção automática (casos de erro)
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Simular QR Code ausente, múltiplo, ilegível ou fora do padrão | Exibe mensagem de erro e permanece/retorna à tela "Escanear QR Code" | |
| 2 | Simular leitura duvidosa da folha de respostas | Exibe mensagem de erro pedindo nova leitura e retorna à tela "Escanear Folha de Respostas" | |

### CT09 — Resultados e estatísticas
| Passo | Ação | Resultado esperado | Status |
|---|---|---|---|
| 1 | Painel → "Ver resultados" (ou menu lateral) | Abre a tela Resultados com lista de resultados | |
| 2 | Abrir um resultado da lista | Abre "Detalhe do resultado" (respostas e nota) | |
| 3 | No Detalhe, clicar "Voltar" | Retorna à tela Resultados | |
| 4 | Acessar "Estatísticas" | Exibe estatísticas por questão e da turma | |
| 5 | Nas Estatísticas, clicar "Voltar" | Retorna à tela Resultados | |

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
| 14 | `<preencher>` | `<preencher>` | `<preencher>` | `<preencher>` |

**Critério de aceite:** 100% dos testes aprovados no ambiente online.

### Falhas encontradas (se houver)
| ID do caso | Descrição da falha | Severidade | Status da correção |
|---|---|---|---|
