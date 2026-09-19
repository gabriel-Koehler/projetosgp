"""
Script de automação para criação de Issues e Labels no repositório GitHub projetosgp.
Requer: Token do GitHub com escopo 'repo'.
Uso:
    python scripts/create_github_issues_kanban.py SEU_GITHUB_TOKEN
"""

import sys
import json
import urllib.request
import urllib.error

REPO = "gabriel-Koehler/projetosgp"
API_URL = f"https://api.github.com/repos/{REPO}"

LABELS = [
    {"name": "n1", "color": "1f77b4", "description": "Fase 01 - Telas Navegáveis e Mockadas"},
    {"name": "n2", "color": "2ca02c", "description": "Fase 02 - Integração Supabase e OMR Python"},
    {"name": "frontend", "color": "e377c2", "description": "Atividades de Front-end & Mocks (Gabriel Koehler)"},
    {"name": "backend", "color": "ff7f0e", "description": "Atividades de Back-end e Banco (Luan Eliseu)"},
    {"name": "documentacao", "color": "17becf", "description": "Documentação e Arquitetura (Alyson Oliveira)"},
    {"name": "requisitos", "color": "bcbd22", "description": "Requisitos e Testes (Eloisa Rocha)"},
    {"name": "infra", "color": "7f7f7f", "description": "Deploy, DER e Supabase (Diego Dornelles)"},
    {"name": "prioridade-p0", "color": "d62728", "description": "Prioridade P0 - Crítica / Bloqueante"},
    {"name": "prioridade-p1", "color": "bcbd22", "description": "Prioridade P1 - Alta"},
    {"name": "criterio-c1", "color": "8c564b", "description": "Critério C1 - Código Compactado .zip"},
    {"name": "criterio-c2", "color": "9467bd", "description": "Critério C2 - Sistema Hospedado"},
    {"name": "criterio-c3", "color": "393b79", "description": "Critério C3 - Documentação README"}
]

ISSUES = [
    # FASE 01 — N1
    {
        "title": "[N1-DOC-01] Esboço Inicial das Classes de Domínio do Sistema",
        "labels": ["n1", "documentacao", "prioridade-p0", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N1-DOC-01 | **Prioridade:** P0 | **Etapa:** Passo 02 (Briefing e Classes de Domínio)
* **Responsável:** ALYSON DE LIMA DE OLIVEIRA

### 🎯 Requisito / Atividade
* Passo 02 do Escopo N1.

### 📝 Descrição Detalhada
1. Analisar o relato do cliente e documento de requisitos.
2. Criar `docs/arquitetura/classes-de-dominio-n1.md` com as entidades: `Professor`, `Semestre`, `Turma`, `Aluno`, `Questao`, `Alternativa`, `Avaliacao`, `VersaoAvaliacao`, `FolhaResposta`, `Gabarito` e `ResultadoCorrecao`.

### 🌿 Branch
`docs/n1-doc-01-classes-dominio`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N1-DOC-01] Esboço inicial das classes de domínio`
* **Revisor:** Eloisa Fazzio da Silva Rocha
* **Critério de Aceite:** Documento aprovado e mergeado na `main`."""
    },
    {
        "title": "[N1-REQ-01] Mapeamento dos Fluxos de Usuário e Casos de Uso",
        "labels": ["n1", "requisitos", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-REQ-01 | **Prioridade:** P0 | **Etapa:** Passo 02 (Briefing e Classes de Domínio)
* **Responsável:** ELOISA FAZZIO DA SILVA ROCHA

### 🎯 Requisito / Atividade
* Fluxos 9 e 10 do documento de requisitos, Passo 04 da N1.

### 📝 Descrição Detalhada
1. Criar `docs/requisitos/fluxos-de-usuario.md` documentando a jornada do Professor e do Aluno.
2. Mapear a regra de navegação: "a tela A leva à tela B", sem pontas soltas.

### 🌿 Branch
`docs/n1-req-01-fluxos-casos-uso`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N1-REQ-01] Mapeamento dos fluxos de navegação e casos de uso`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Diagramas Mermaid aprovados e merge na `main`."""
    },
    {
        "title": "[N1-INF-03] Configuração do Repositório, Labels, Templates e Quadro Kanban",
        "labels": ["n1", "infra", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-INF-03 | **Prioridade:** P0 | **Etapa:** Passo 03 (Repositório GitHub e Issues)
* **Responsável:** GABRIEL KOEHLER DA SILVA

### 🎯 Requisito / Atividade
* Passo 03 do Escopo N1.

### 📝 Descrição Detalhada
1. Configurar o repositório GitHub com labels padronizadas.
2. Implementar template oficial de issues em `.github/ISSUE_TEMPLATE/card-atividade.md`.
3. Estruturar o Quadro Kanban em `docs/KANBAN_BOARD.md` e script de automação (`scripts/create_github_issues_kanban.py`).

### 🌿 Branch
`infra/n1-inf-03-setup-repo-kanban`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N1-INF-03] Configuração do repositório, issues, labels e quadro Kanban`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Template e quadro Kanban aprovados e merge na `main`."""
    },
    {
        "title": "[N1-BE-01] Estruturação da API Python (FastAPI) e Sessão de Autenticação",
        "labels": ["n1", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-BE-01 | **Prioridade:** P0 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF01, RNF06, RNF09.

### 📝 Descrição Detalhada
1. Inicializar backend Python modular (`app/main.py`, `app/routers/`, `app/core/`, `requirements.txt`).
2. Criar rotas de autenticação do professor com controle de sessão e proteção das rotas administrativas.

### 🌿 Branch
`feat/n1-be-01-setup-api-python-auth`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N1-BE-01] Setup da API Python com FastAPI e login do professor`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Servidor rodando localmente com uvicorn e bloqueio de rotas sem autenticação."""
    },
    {
        "title": "[N1-FE-01] Layout Base, Design System e Tela de Autenticação",
        "labels": ["n1", "frontend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-01 | **Prioridade:** P0 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF01, RNF01, RNF02, RNF03.

### 📝 Descrição Detalhada
1. Construir layout padrão (header, navegação, barra superior, logout, footer e `public/styles.css`).
2. Implementar tela de login minimalista e responsiva com feedback visual de credenciais inválidas.

### 🌿 Branch
`feat/n1-fe-01-layout-login`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-01] Implementa layout base responsivo e tela de login`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Interface responsiva e transição limpa para `/dashboard`."""
    },
    {
        "title": "[N1-BE-02] Provedor de Dados Estruturados em Memória (Python Mock State)",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-BE-02 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** GABRIEL KOEHLER DA SILVA

### 🎯 Requisito / Atividade
* RF02, RF03, RF04, RF06, RF09.

### 📝 Descrição Detalhada
1. Criar módulo `app/mocks/data_provider.py` com listas em memória de semestres, turmas, alunos e questões.
2. Disponibilizar endpoints mockados (`/api/semestres`, `/api/turmas`, `/api/questoes`).

### 🌿 Branch
`feat/n1-be-02-python-mock-state`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(mock): [N1-BE-02] Provedor de dados mock estruturados em Python`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Endpoints respondendo JSON válido para o front-end."""
    },
    {
        "title": "[N1-FE-02] Interface de Gestão de Semestres e Turmas (Navegável com Mocks)",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-02 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF02, RF03.

### 📝 Descrição Detalhada
1. Criar tela de Semestres (listagem e cadastro simulado).
2. Criar tela de Turmas com filtro/vínculo por semestre e cards informativos.

### 🌿 Branch
`feat/n1-fe-02-semestres-turmas`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-02] Telas navegáveis de semestres e turmas`
* **Revisor:** Eloisa Fazzio da Silva Rocha
* **Critério de Aceite:** Telas navegáveis sem links quebrados."""
    },
    {
        "title": "[N1-FE-03] Interface de Gestão e Importação de Alunos",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-03 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF04, RF05.

### 📝 Descrição Detalhada
1. Desenvolver listagem de alunos da turma, modal de inclusão manual e interface de importação em lote com upload de planilha simulado, download de modelo (`modelo_alunos.csv`) e pré-visualização.

### 🌿 Branch
`feat/n1-fe-03-alunos-importacao`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-03] Interface de alunos e modal de importação com prévia`
* **Revisor:** Diego Rafael da Silva Dornelles
* **Critério de Aceite:** Prévia simulando validação visual de alunos."""
    },
    {
        "title": "[N1-FE-04] Interface Completa do Banco de Questões (CRUD e Importação)",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-04 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF06 a RF13.

### 📝 Descrição Detalhada
1. Desenvolver tela do Banco de Questões com busca por texto e filtros rápidos.
2. Modal/Formulário para inclusão e edição de questões com alternativas A-D e gabarito destacado.
3. Importação em lote por planilha com prévia e download do modelo template.

### 🌿 Branch
`feat/n1-fe-04-banco-questoes`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-04] Tela do banco de questões, filtros e importação em lote`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Alternativas recolhíveis e gabarito visível."""
    },
    {
        "title": "[N1-BE-03] Core Python: Embaralhamento e Preservação de Gabaritos",
        "labels": ["n1", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-BE-03 | **Prioridade:** P0 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF17 a RF25, RN06, RN07, RN25.

### 📝 Descrição Detalhada
1. Implementar em Python (`app/core/version_builder.py`) a função de geração de versões parametrizadas.
2. Garantir que o embaralhamento de alternativas atualize o gabarito oficial da versão. Testes com `pytest`.

### 🌿 Branch
`feat/n1-be-03-python-core-embaralhamento`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N1-BE-03] Lógica central em Python para embaralhamento e gabaritos`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** 100% de sucesso nos testes de permutação."""
    },
    {
        "title": "[N1-BE-04] Geração de QR Code e Rota de Consulta Restrita do Aluno",
        "labels": ["n1", "backend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-BE-04 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF28 a RF30, RN03 a RN05.

### 📝 Descrição Detalhada
1. Gerador de QR Code em Python (`qrcode` + `Pillow`) codificando a URL da versão.
2. Rota pública `/student/gabarito` exibindo estritamente as alternativas corretas, sem dados sensíveis.

### 🌿 Branch
`feat/n1-be-04-python-qrcode-aluno`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N1-BE-04] Geração de QR Code e rota pública restrita do gabarito`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** QR Code legível abrindo tela higienizada do aluno."""
    },
    {
        "title": "[N1-FE-05] Assistente de Criação de Avaliações e Configuração de Versões",
        "labels": ["n1", "frontend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-05 | **Prioridade:** P0 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF14 a RF25.

### 📝 Descrição Detalhada
1. Assistente em 3 etapas: seleção de turma, seleção de questões com contador e configuração de versões (nomes, embaralhamento).
2. Tela de confirmação com cards interativos das versões geradas.

### 🌿 Branch
`feat/n1-fe-05-criacao-avaliacoes-versoes`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-05] Assistente de criação de avaliações e configuração de versões`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Navegação completa e sem erros."""
    },
    {
        "title": "[N1-FE-06] Interface de Impressão de Provas, Folha de Respostas e Tela Aluno",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-06 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF26 a RF30.

### 📝 Descrição Detalhada
1. Layout de Prova diagramada para impressão (`@media print`).
2. Layout para impressão da Folha de Respostas com QR Code e bolinhas A-D.
3. Estilização da página pública do aluno.

### 🌿 Branch
`feat/n1-fe-06-impressao-prova-aluno`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-06] Telas de impressão de prova, folha de respostas e área do aluno`
* **Revisor:** Eloisa Fazzio da Silva Rocha
* **Critério de Aceite:** Impressão limpa e tela do aluno responsiva."""
    },
    {
        "title": "[N1-FE-07] Interface de Simulação de Correção de Provas, Resultados e Estatísticas",
        "labels": ["n1", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-FE-07 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF31, RF34, RF36, RF41 a RF48.

### 📝 Descrição Detalhada
1. Tela de simulação de "Corrigir Prova" (upload e feedback visual de leitura).
2. Painel de Resultados por aluno e notas calculadas.
3. Painel de Estatísticas com taxa de acerto por questão e alternativa mais assinalada.

### 🌿 Branch
`feat/n1-fe-07-correcao-estatisticas`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N1-FE-07] Interfaces de correção simulada, resultados e estatísticas`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Simulação visual completa do fluxo pós-prova."""
    },
    {
        "title": "[N1-REQ-02] Roteiro e Execução de Testes Navegáveis de Aceitação",
        "labels": ["n1", "requisitos", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-REQ-02 | **Prioridade:** P1 | **Etapa:** Passo 04 (Telas Navegáveis com Mock)
* **Responsável:** ELOISA FAZZIO DA SILVA ROCHA

### 🎯 Requisito / Atividade
* Critério C2 da N1.

### 📝 Descrição Detalhada
1. Criar `docs/testes/roteiro-testes-n1.md` com casos de teste navegáveis de ponta a ponta.
2. Executar testes no ambiente hospedado e registrar relatório de aceitação.

### 🌿 Branch
`test/n1-req-02-testes-aceitacao-navegavel`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `test: [N1-REQ-02] Roteiro e relatório de execução dos testes navegáveis N1`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** 100% dos testes aprovados no ambiente online."""
    },
    {
        "title": "[N1-DOC-02] Elaboração do README v1 Oficial (Critério C3 da N1)",
        "labels": ["n1", "documentacao", "prioridade-p1", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N1-DOC-02 | **Prioridade:** P1 | **Etapa:** Passo 06 (README v1 conforme modelo_doc.md)
* **Responsável:** ALYSON DE LIMA DE OLIVEIRA

### 🎯 Requisito / Atividade
* Critério C3 (20% da N1), Passo 06.

### 📝 Descrição Detalhada
1. Redigir `README.md` v1 oficial: visão geral, escopo da N1, requisitos RF/RNF, galeria de screenshots, guia de execução local em Python e link do sistema hospedado.

### 🌿 Branch
`docs/n1-doc-02-readme-v1`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N1-DOC-02] Elaboração do README v1 oficial da fase N1`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** README completo sem links quebrados."""
    },
    {
        "title": "[N1-INF-01] Configuração de Hospedagem Contínua Gratuita (Render / Vercel)",
        "labels": ["n1", "infra", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N1-INF-01 | **Prioridade:** P0 | **Etapa:** Passo 08 (Hospedagem Gratuita)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Critério C2 (20% da N1), Passo 08.

### 📝 Descrição Detalhada
1. Configurar pipeline de deploy contínuo em nuvem gratuita para a aplicação Python/FastAPI.
2. Validar acesso público via HTTPS e registrar a URL pública no repositório.

### 🌿 Branch
`infra/n1-inf-01-deploy-hospedagem`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N1-INF-01] Pipeline de deploy contínuo na nuvem N1`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Link HTTPS público respondendo com status 200."""
    },
    {
        "title": "[N1-INF-02] Automação do Pacote C1 (.zip limpo) e Auditoria Final N1",
        "labels": ["n1", "infra", "prioridade-p0", "criterio-c1"],
        "body": """### 📌 Identificação
* **ID:** N1-INF-02 | **Prioridade:** P0 | **Etapa:** Passo 09 (Pacote de Entrega N1)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Critério C1 (10% da N1), Passo 09.

### 📝 Descrição Detalhada
1. Criar script `scripts/package_delivery.py` para compactar o projeto em `.zip` excluindo pastas desnecessárias (`venv/`, `__pycache__/`, `.git/`).
2. Auditar repositório garantindo zero PRs abertos.

### 🌿 Branch
`infra/n1-inf-02-script-empacotamento-c1`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N1-INF-02] Script de empacotamento .zip C1 e auditoria final de PRs N1`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Arquivo zip limpo e zero pendências de PR na `main`."""
    },

    # FASE 02 — N2
    {
        "title": "[N2-BE-01] Implementação da Arquitetura em Camadas em Python",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-01 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RNF08, RNF09, Passo 01 da N2.

### 📝 Descrição Detalhada
1. Reorganizar backend Python na arquitetura em camadas: `app/controllers/`, `app/services/`, `app/repositories/` e `app/models/`.

### 🌿 Branch
`feat/n2-be-01-arquitetura-camadas-python`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-01] Estruturação da arquitetura em camadas em Python`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Estrutura modular desacoplada sem dependências circulares."""
    },
    {
        "title": "[N2-BE-02] Configuração do Conector Supabase e Pool de Conexões",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-02 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RNF08, Passo 01 da N2.

### 📝 Descrição Detalhada
1. Configurar cliente Supabase (`supabase-py`) e pool PostgreSQL (`DATABASE_URL`). Implementar rotina de migração e conectividade `app/database/migrate.py`.

### 🌿 Branch
`feat/n2-be-02-supabase-client-pool`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-02] Conexão pool com Supabase (PostgreSQL) e rotina de teste`
* **Revisor:** Diego Rafael da Silva Dornelles
* **Critério de Aceite:** Conexão com Supabase validada."""
    },
    {
        "title": "[N2-BE-03] Implementação dos Repositories e Services CRUD sobre o Supabase",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-03 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF01 a RF13.

### 📝 Descrição Detalhada
1. Implementar Repositories e Services CRUD para Professores, Semestres, Turmas, Alunos e Questões/Alternativas sobre o Supabase.

### 🌿 Branch
`feat/n2-be-03-crud-repositories-supabase`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-03] Repositories e Services de cadastros básicos sobre Supabase`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Operações no banco real confirmadas."""
    },
    {
        "title": "[N2-FE-01] Conexão Real da Autenticação e Semestres/Turmas com a API",
        "labels": ["n2", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-FE-01 | **Prioridade:** P1 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF01, RF02, RF03, Critério C2 da N2.

### 📝 Descrição Detalhada
1. Conectar telas de login, semestres e turmas à API Python integrada ao Supabase com tratamento visual de erros.

### 🌿 Branch
`feat/n2-fe-01-integracao-auth-turmas`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N2-FE-01] Conecta telas de autenticação e turmas ao backend com Supabase`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Dados persistem e recarregam do banco."""
    },
    {
        "title": "[N2-FE-02] Conexão Real do Banco de Questões e Upload de Arquivos",
        "labels": ["n2", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-FE-02 | **Prioridade:** P1 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF06 a RF13, Critério C2 da N2.

### 📝 Descrição Detalhada
1. Conectar CRUD de questões e upload de planilhas à API real com gravação direta no Supabase.

### 🌿 Branch
`feat/n2-fe-02-integracao-questoes-upload`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N2-FE-02] Integração real do CRUD de questões e importação em lote`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Gravação direta de questões no Supabase."""
    },
    {
        "title": "[N2-BE-04] Persistência Transacional de Avaliações, Versões e Gabaritos no Supabase",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-04 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF14 a RF25, RN06, RN07, RN14.

### 📝 Descrição Detalhada
1. Método transacional: grava avaliação, gera versões com embaralhamento e insere atomicamente em `versao_avaliacao`, `questao_versao` e `gabarito_versao`.

### 🌿 Branch
`feat/n2-be-04-transacoes-avaliacoes-versoes`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-04] Persistência transacional de avaliações, versões e gabaritos no Supabase`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Transação atômica confirmada no Supabase."""
    },
    {
        "title": "[N2-FE-03] Conexão da Criação de Avaliações e Persistência de Versões",
        "labels": ["n2", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-FE-03 | **Prioridade:** P1 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF14 a RF25, Critério C2 da N2.

### 📝 Descrição Detalhada
1. Conectar assistente de avaliações para buscar questões e enviar configurações de versões para a API Python, renderizando versões salvas no banco com QR Codes dinâmicos.

### 🌿 Branch
`feat/n2-fe-03-integracao-avaliacoes-versoes`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N2-FE-03] Integração da criação e geração de versões com o banco real`
* **Revisor:** Diego Rafael da Silva Dornelles
* **Critério de Aceite:** Versões recuperadas diretamente do Supabase."""
    },
    {
        "title": "[N2-BE-05] Módulo de Processamento de Imagem OMR (OpenCV) e Leitura de QR Code",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-05 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF31 a RF37, RF40.

### 📝 Descrição Detalhada
1. Serviço `app/services/omr_service.py` com OpenCV e pyzbar: decodificar QR Code, segmentar alternativas e detectar bolinhas marcadas com validação de rasuras.

### 🌿 Branch
`feat/n2-be-05-python-opencv-omr`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-05] Módulo de Visão Computacional (OpenCV/pyzbar) para correção OMR`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Detecção correta em imagens teste da folha."""
    },
    {
        "title": "[N2-BE-06] Cálculo de Notas, Persistência no Supabase e Exportação Excel",
        "labels": ["n2", "backend", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-BE-06 | **Prioridade:** P0 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Luan Eliseu

### 🎯 Requisito / Atividade
* RF38, RF39, RF44 a RF48.

### 📝 Descrição Detalhada
1. Comparar respostas detectadas com `gabarito_versao`, calcular nota e persistir resultado no Supabase. Endpoint para download de planilha Excel formatada.

### 🌿 Branch
`feat/n2-be-06-calculo-notas-exportacao-excel`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(back): [N2-BE-06] Cálculo de notas, persistência de correção no Supabase e exportação Excel`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Notas corretas gravadas e planilha funcional."""
    },
    {
        "title": "[N2-FE-04] Interface de Correção Real e Download de Relatório Excel",
        "labels": ["n2", "frontend", "prioridade-p1", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-FE-04 | **Prioridade:** P1 | **Etapa:** Passo 01 (Banco Real e Camadas)
* **Responsável:** Gabriel Koehler da Silva

### 🎯 Requisito / Atividade
* RF31, RF41 a RF48, Critério C2 da N2.

### 📝 Descrição Detalhada
1. Conectar tela de correção para envio da imagem ao endpoint OMR via multipart. Exibir nota calculada, estatísticas da turma e botão de download do relatório Excel oficial.

### 🌿 Branch
`feat/n2-fe-04-integracao-correcao-excel`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `feat(front): [N2-FE-04] Integração da correção OMR real e download de relatório Excel`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Correção real funcional e download da planilha."""
    },
    {
        "title": "[N2-MER-01] Elaboração do Modelo Entidade-Relacionamento Conceitual (MER)",
        "labels": ["n2", "requisitos", "prioridade-p0", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-MER-01 | **Prioridade:** P0 | **Etapa:** Passo 02 (Modelar Banco e ADRs)
* **Responsável:** ELOISA FAZZIO DA SILVA ROCHA

### 🎯 Requisito / Atividade
* Passo 02 e Critério C3 da N2.

### 📝 Descrição Detalhada
1. Desenvolver o MER conceitual em `docs/banco-de-dados/mer-conceitual.md` com entidades e cardinalidades.

### 🌿 Branch
`docs/n2-mer-01-diagrama-mer-conceitual`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N2-MER-01] Elaboração do modelo entidade-relacionamento (MER) conceitual`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Diagrama Mermaid detalhado aprovado."""
    },
    {
        "title": "[N2-MER-02] Dicionário de Dados e Regras de Integridade para Supabase",
        "labels": ["n2", "requisitos", "prioridade-p1", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-MER-02 | **Prioridade:** P1 | **Etapa:** Passo 02 (Modelar Banco e ADRs)
* **Responsável:** ELOISA FAZZIO DA SILVA ROCHA

### 🎯 Requisito / Atividade
* Passo 02 e Critério C3 da N2.

### 📝 Descrição Detalhada
1. Documentar em `docs/banco-de-dados/dicionario-de-dados.md` todas as tabelas, colunas, tipos PostgreSQL/Supabase, constraints e regras de integridade.

### 🌿 Branch
`docs/n2-mer-02-dicionario-dados-integridade`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N2-MER-02] Dicionário de dados completo e regras de integridade para Supabase`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Documento aprovado cobrindo todos os atributos."""
    },
    {
        "title": "[N2-INF-01] Provisionamento do Projeto no Supabase, DER Físico e Scripts DDL",
        "labels": ["n2", "infra", "prioridade-p0", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-INF-01 | **Prioridade:** P0 | **Etapa:** Passo 02 (Modelar Banco e ADRs)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Passo 02 e Critério C3 da N2.

### 📝 Descrição Detalhada
1. Criar projeto no Supabase, documentar `.env.example`, elaborar DER físico e escrever scripts SQL PostgreSQL `src/database/schema.sql` e `src/database/seed.sql`. Executar no Supabase.

### 🌿 Branch
`infra/n2-inf-01-supabase-der-ddl-seed`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N2-INF-01] Provisionamento do Supabase, DER físico e scripts DDL (schema) e Seed`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Tabelas criadas no Supabase e scripts versionados."""
    },
    {
        "title": "[N2-DOC-01] Documentação da Arquitetura em Camadas e Decisões Técnicas (ADRs)",
        "labels": ["n2", "documentacao", "prioridade-p1", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-DOC-01 | **Prioridade:** P1 | **Etapa:** Passo 02 (Modelar Banco e ADRs)
* **Responsável:** ALYSON DE LIMA DE OLIVEIRA

### 🎯 Requisito / Atividade
* Passo 02 e Critério C3 (20% da N2).

### 📝 Descrição Detalhada
1. Documentar `docs/arquitetura/arquitetura-em-camadas.md` e registrar ADRs fundamentando a escolha do Python/OpenCV e do Supabase.

### 🌿 Branch
`docs/n2-doc-01-arquitetura-camadas-adr`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N2-DOC-01] Documentação da arquitetura em camadas e registros de decisão (ADRs)`
* **Revisor:** Luan Eliseu
* **Critério de Aceite:** Documento arquitetural aprovado."""
    },
    {
        "title": "[N2-INF-02] Elaboração do Diagrama de Classes UML v2 Atualizado",
        "labels": ["n2", "infra", "prioridade-p1", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-INF-02 | **Prioridade:** P1 | **Etapa:** Passo 03 (Classes de Domínio e UML v2)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Critério C3 (20% da N2), Passo 03 da N2.

### 📝 Descrição Detalhada
1. Elaborar Diagrama de Classes UML v2 em `docs/arquitetura/diagrama-classes-uml-v2.md` refletindo as classes Python implementadas.

### 🌿 Branch
`docs/n2-inf-02-diagrama-classes-uml-v2`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N2-INF-02] Diagrama de classes UML v2 em conformidade com o código Python`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Diagrama reflete 100% da estrutura implementada."""
    },
    {
        "title": "[N2-DOC-02] Atualização Oficial do README para a Versão v2",
        "labels": ["n2", "documentacao", "prioridade-p1", "criterio-c3"],
        "body": """### 📌 Identificação
* **ID:** N2-DOC-02 | **Prioridade:** P1 | **Etapa:** Passo 05 (README v2 Oficial)
* **Responsável:** ALYSON DE LIMA DE OLIVEIRA

### 🎯 Requisito / Atividade
* Critério C3 (20% da N2), Passo 05.

### 📝 Descrição Detalhada
1. Atualizar `README.md` para v2 oficial com arquitetura em camadas, backend Python com OpenCV/OMR, banco Supabase, diagramas MER, DER e UML v2, variáveis `.env` e link de produção.

### 🌿 Branch
`docs/n2-doc-02-readme-v2`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `docs: [N2-DOC-02] Atualização do README oficial para versão v2 da N2 com Supabase`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** README v2 completo conforme a disciplina."""
    },
    {
        "title": "[N2-INF-03] Configuração de Produção do Supabase e Atualização do Deploy Hospedado",
        "labels": ["n2", "infra", "prioridade-p0", "criterio-c2"],
        "body": """### 📌 Identificação
* **ID:** N2-INF-03 | **Prioridade:** P0 | **Etapa:** Passo 07 (Republicar Sistema)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Critério C2 (40% da N2), Passo 07.

### 📝 Descrição Detalhada
1. Configurar variáveis do Supabase no provedor de nuvem e certificar que a aplicação em produção opera sem nenhum dado mock.

### 🌿 Branch
`infra/n2-inf-03-supabase-cloud-deploy-n2`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N2-INF-03] Configuração de produção com Supabase e republicação do sistema N2`
* **Revisor:** Gabriel Koehler da Silva
* **Critério de Aceite:** Sistema online operando 100% sobre o Supabase sem mocks."""
    },
    {
        "title": "[N2-INF-04] Pacote de Entrega C1 (.zip) e Homologação Final N2",
        "labels": ["n2", "infra", "prioridade-p0", "criterio-c1"],
        "body": """### 📌 Identificação
* **ID:** N2-INF-04 | **Prioridade:** P0 | **Etapa:** Passo 08 (Entrega N2)
* **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES

### 🎯 Requisito / Atividade
* Critério C1 (10% da N2), Passo 08.

### 📝 Descrição Detalhada
1. Gerar arquivo `.zip` limpo da fase N2, testar descompactação e validar conformidade com os critérios C1, C2 e C3.

### 🌿 Branch
`infra/n2-inf-04-pacote-entrega-n2`

### 🔄 Ciclo Obrigatório de Entrega (PR e Merge)
* **Título do PR:** `infra: [N2-INF-04] Pacote .zip C1 e homologação final N2`
* **Revisor:** Alyson de Lima de Oliveira
* **Critério de Aceite:** Arquivo zip gerado limpo e aprovado."""
    }
]

def request(url, token, data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "antigravity-setup-script"
    }
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"Erro HTTP {e.code} em {url}: {err_msg}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/create_github_issues_kanban.py SEU_GITHUB_TOKEN")
        sys.exit(1)
    
    token = sys.argv[1]
    print(f"Criando labels no repositório {REPO}...")
    for label in LABELS:
        res = request(f"{API_URL}/labels", token, label)
        if res:
            print(f"  [+] Label '{label['name']}' criada com sucesso.")
        else:
            print(f"  [-] Label '{label['name']}' já existia ou erro ao criar.")

    print(f"\nCriando {len(ISSUES)} issues oficiais no repositório {REPO} (N1 e N2)...")
    for idx, issue in enumerate(ISSUES, 1):
        payload = {
            "title": issue["title"],
            "body": issue["body"],
            "labels": issue["labels"]
        }
        res = request(f"{API_URL}/issues", token, payload)
        if res:
            print(f"  [{idx:02d}/{len(ISSUES)}] Issue #{res['number']} '{issue['title']}' criada!")
        else:
            print(f"  [{idx:02d}/{len(ISSUES)}] Erro ao criar issue '{issue['title']}'.")

    print("\nProcesso concluído com sucesso!")

if __name__ == "__main__":
    main()
