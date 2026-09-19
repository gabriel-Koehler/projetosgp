# 📋 BACKLOG TÉCNICO DETALHADO DO PROJETO (ETAPAS N1 E N2)

Este documento contém o detalhamento técnico e operacional de todos os **32 cards de atividades** do repositório **[projetosgp](https://github.com/gabriel-Koehler/projetosgp.git)**, organizados pelas etapas do documento oficial **"Escopo do Projeto e Critérios de Avaliação"**.

---

## 👥 Matriz de Responsabilidades
* 🎨 **Front-end & Mocks/Setup:** Gabriel Koehler da Silva
* ⚙️ **Back-end & Banco de Dados:** Luan Eliseu (Python FastAPI + Supabase + OpenCV)
* 📄 **Documentação & Arquitetura:** ALYSON DE LIMA DE OLIVEIRA
* 📐 **Requisitos & Testes:** ELOISA FAZZIO DA SILVA ROCHA
* 🚀 **Infraestrutura, Deploy & DER:** DIEGO RAFAEL DA SILVA DORNELLES

---

## 🔄 Ciclo Obrigatório de Entrega de Cada Card
1. **Branch própria:** `git checkout main && git pull origin main && git checkout -b <nome-da-branch>`
2. **Commits semânticos:** `git commit -m "tipo(escopo): descrição [ID-CARD]"`
3. **Pull Request (PR):** Aberto contra a `main` com evidências e checklist.
4. **Code Review:** Avaliação e aprovação do colega designado como revisor.
5. **Merge na Main:** Integração do código aprovado à branch principal.

---

# 📦 FASE 01 — N1: Telas Navegáveis e Mockadas

### 🔹 Passo 02: Briefing e Classes de Domínio

#### 📌 [N1-DOC-01] Esboço Inicial das Classes de Domínio do Sistema
* **Prioridade:** `P0 (Crítica)` | **Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Requisitos Atendidos:** Passo 02 do Escopo N1.
* **Descrição Detalhada:**
  1. Analisar o relato do cliente e o documento de requisitos.
  2. Criar `docs/arquitetura/classes-de-dominio-n1.md` com as 11 entidades conceituais: `Professor`, `Semestre`, `Turma`, `Aluno`, `Questao`, `Alternativa`, `Avaliacao`, `VersaoAvaliacao`, `FolhaResposta`, `Gabarito` e `ResultadoCorrecao`.
  3. Descrever atributos, tipos e relacionamentos de cada classe.
* **Branch:** `docs/n1-doc-01-classes-dominio`
* **Pull Request:** Título `docs: [N1-DOC-01] Esboço inicial das classes de domínio` | Revisor: Eloisa Fazzio da Silva Rocha.

#### 📌 [N1-REQ-01] Mapeamento dos Fluxos de Usuário e Casos de Uso
* **Prioridade:** `P0 (Crítica)` | **Responsável:** ELOISA FAZZIO DA SILVA ROCHA
* **Requisitos Atendidos:** Fluxos 9 e 10 do documento de requisitos, Passo 04 da N1.
* **Descrição Detalhada:**
  1. Criar `docs/requisitos/fluxos-de-usuario.md` mapeando a experiência do Professor (Login, Gestão, Criação da Prova, Correção e Relatórios) e do Aluno (QR Code ao Gabarito).
  2. Mapear a regra de navegação "a tela A leva à tela B" para guiar o front-end.
* **Branch:** `docs/n1-req-01-fluxos-casos-uso`
* **Pull Request:** Título `docs: [N1-REQ-01] Mapeamento dos fluxos de navegação e casos de uso` | Revisor: Gabriel Koehler da Silva.

---

### 🔹 Passo 03: Repositório GitHub e Estruturação das Issues

#### 📌 [N1-INF-03] Configuração do Repositório, Labels, Templates e Quadro Kanban
* **Prioridade:** `P0 (Crítica)` | **Responsável:** GABRIEL KOEHLER DA SILVA
* **Requisitos Atendidos:** Passo 03 do Escopo N1.
* **Descrição Detalhada:**
  1. Configurar labels do repositório no GitHub (`n1`, `n2`, `frontend`, `backend`, `documentacao`, `infra`, `prioridade-p0`, `prioridade-p1`, `criterio-c1`, `criterio-c2`, `criterio-c3`).
  2. Criar template oficial de issues em `.github/ISSUE_TEMPLATE/card-atividade.md`.
  3. Estruturar o Quadro Kanban em `docs/KANBAN_BOARD.md` e script de carga de issues (`scripts/create_github_issues_kanban.py`).
* **Branch:** `infra/n1-inf-03-setup-repo-kanban`
* **Pull Request:** Título `infra: [N1-INF-03] Configuração do repositório, issues, labels e quadro Kanban` | Revisor: Alyson de Lima de Oliveira.

---

### 🔹 Passo 04: Construção das Telas Navegáveis com Dados Mock

#### 📌 [N1-BE-01] Estruturação da API Python (FastAPI) e Sessão de Autenticação
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF01, RNF06, RNF09.
* **Descrição Detalhada:**
  1. Inicializar estrutura Python modular: `app/main.py`, `app/routers/`, `app/core/`, `requirements.txt`.
  2. Implementar rotas de login do professor e middleware de controle de sessão seguro.
  3. Bloquear rotas administrativas para usuários não autenticados.
* **Branch:** `feat/n1-be-01-setup-api-python-auth`
* **Pull Request:** Título `feat(back): [N1-BE-01] Setup da API Python com FastAPI e login do professor` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N1-FE-01] Layout Base, Design System e Tela de Autenticação
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF01, RNF01, RNF02, RNF03.
* **Descrição Detalhada:**
  1. Construir layout padrão (header, navbar com nome do professor e botão de logout, footer e estilos globais em `public/styles.css`).
  2. Implementar tela de login responsiva e minimalista com feedback visual de credenciais inválidas.
* **Branch:** `feat/n1-fe-01-layout-login`
* **Pull Request:** Título `feat(front): [N1-FE-01] Implementa layout base responsivo e tela de login` | Revisor: Luan Eliseu.

#### 📌 [N1-BE-02] Provedor de Dados Estruturados em Memória (Python Mock State)
* **Prioridade:** `P1 (Alta)` | **Responsável:** GABRIEL KOEHLER DA SILVA
* **Requisitos Atendidos:** RF02, RF03, RF04, RF06, RF09.
* **Descrição Detalhada:**
  1. Criar `app/mocks/data_provider.py` com listas em memória de semestres, turmas, alunos e questões (enunciados, opções A-D e resposta correta).
  2. Implementar endpoints mockados (`/api/semestres`, `/api/turmas`, `/api/questoes`) para abastecer o front-end.
* **Branch:** `feat/n1-be-02-python-mock-state`
* **Pull Request:** Título `feat(mock): [N1-BE-02] Provedor de dados mock estruturados em Python` | Revisor: Luan Eliseu.

#### 📌 [N1-FE-02] Interface de Gestão de Semestres e Turmas (Navegável com Mocks)
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF02, RF03.
* **Descrição Detalhada:**
  1. Desenvolver tela de listagem e cadastro de semestres letivos.
  2. Desenvolver tela de turmas vinculadas ao semestre selecionado com navegação navegável fluida entre as visões.
* **Branch:** `feat/n1-fe-02-semestres-turmas`
* **Pull Request:** Título `feat(front): [N1-FE-02] Telas navegáveis de semestres e turmas` | Revisor: Eloisa Fazzio da Silva Rocha.

#### 📌 [N1-FE-03] Interface de Gestão e Importação de Alunos
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF04, RF05.
* **Descrição Detalhada:**
  1. Desenvolver listagem de alunos da turma selecionada.
  2. Modal de inclusão individual de aluno.
  3. Interface de importação em lote com upload de planilha simulado, download de modelo (`modelo_alunos.csv`) e pré-visualização (preview).
* **Branch:** `feat/n1-fe-03-alunos-importacao`
* **Pull Request:** Título `feat(front): [N1-FE-03] Interface de alunos e modal de importação com prévia` | Revisor: Diego Rafael da Silva Dornelles.

#### 📌 [N1-FE-04] Interface Completa do Banco de Questões (CRUD e Importação)
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF06 a RF13.
* **Descrição Detalhada:**
  1. Desenvolver tela do Banco de Questões com barra de pesquisa por texto e filtros rápidos.
  2. Modal/Formulário para inclusão e edição de questões com alternativas A-D e gabarito destacado.
  3. Importação em lote por planilha com prévia e download do modelo template.
* **Branch:** `feat/n1-fe-04-banco-questoes`
* **Pull Request:** Título `feat(front): [N1-FE-04] Tela do banco de questões, filtros e importação em lote` | Revisor: Luan Eliseu.

#### 📌 [N1-BE-03] Core Python: Embaralhamento e Preservação de Gabaritos
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF17 a RF25, RN06, RN07, RN25.
* **Descrição Detalhada:**
  1. Implementar em Python (`app/core/version_builder.py`) a função pura de geração de versões parametrizadas.
  2. Garantir que o embaralhamento de alternativas recalcule com precisão a posição da resposta correta no gabarito oficial da versão. Testes com `pytest`.
* **Branch:** `feat/n1-be-03-python-core-embaralhamento`
* **Pull Request:** Título `feat(back): [N1-BE-03] Lógica central em Python para embaralhamento e gabaritos` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N1-BE-04] Geração de QR Code e Rota de Consulta Restrita do Aluno
* **Prioridade:** `P1 (Alta)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF28 a RF30, RN03 a RN05.
* **Descrição Detalhada:**
  1. Gerador de QR Code em Python (`qrcode` + `Pillow`) codificando a URL da avaliação e versão.
  2. Rota pública `/student/gabarito` restrita, retornando apenas as alternativas corretas, sem dados sensíveis.
* **Branch:** `feat/n1-be-04-python-qrcode-aluno`
* **Pull Request:** Título `feat(back): [N1-BE-04] Geração de QR Code e rota pública restrita do gabarito` | Revisor: Alyson de Lima de Oliveira.

#### 📌 [N1-FE-05] Assistente de Criação de Avaliações e Configuração de Versões
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF14 a RF25.
* **Descrição Detalhada:**
  1. Assistente em 3 etapas: seleção de turma, seleção de questões com contador dinâmico e configuração de versões (nomes, embaralhamento).
  2. Tela de confirmação com cards interativos das versões geradas.
* **Branch:** `feat/n1-fe-05-criacao-avaliacoes-versoes`
* **Pull Request:** Título `feat(front): [N1-FE-05] Assistente de criação de avaliações e configuração de versões` | Revisor: Alyson de Lima de Oliveira.

#### 📌 [N1-FE-06] Interface de Impressão de Provas, Folha de Respostas e Tela Aluno
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF26 a RF30.
* **Descrição Detalhada:**
  1. Diagramar folha de Prova para impressão (`@media print`).
  2. Diagramar Folha de Respostas com QR Code e bolinhas A-D legíveis para o OMR.
  3. Estilizar interface pública do aluno.
* **Branch:** `feat/n1-fe-06-impressao-prova-aluno`
* **Pull Request:** Título `feat(front): [N1-FE-06] Telas de impressão de prova, folha de respostas e área do aluno` | Revisor: Eloisa Fazzio da Silva Rocha.

#### 📌 [N1-FE-07] Interface de Simulação de Correção de Provas, Resultados e Estatísticas
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF31, RF34, RF36, RF41 a RF48.
* **Descrição Detalhada:**
  1. Tela de simulação de "Corrigir Prova" (upload e feedback visual de leitura).
  2. Painel de Resultados por aluno e notas calculadas.
  3. Painel de Estatísticas com gráficos de taxa de acerto por questão e alternativa mais assinalada.
* **Branch:** `feat/n1-fe-07-correcao-estatisticas`
* **Pull Request:** Título `feat(front): [N1-FE-07] Interfaces de correção simulada, resultados e estatísticas` | Revisor: Luan Eliseu.

#### 📌 [N1-REQ-02] Roteiro e Execução de Testes Navegáveis de Aceitação
* **Prioridade:** `P1 (Alta)` | **Responsável:** ELOISA FAZZIO DA SILVA ROCHA
* **Requisitos Atendidos:** Critério C2 da N1.
* **Descrição Detalhada:**
  1. Elaborar `docs/testes/roteiro-testes-n1.md` com casos de teste navegáveis de ponta a ponta.
  2. Executar testes no ambiente hospedado e registrar relatório de aceitação.
* **Branch:** `test/n1-req-02-testes-aceitacao-navegavel`
* **Pull Request:** Título `test: [N1-REQ-02] Roteiro e relatório de execução dos testes navegáveis N1` | Revisor: Luan Eliseu.

---

### 🔹 Passo 06: Escrever o README v1 (conforme modelo_doc.md)

#### 📌 [N1-DOC-02] Elaboração do README v1 Oficial (Critério C3 da N1)
* **Prioridade:** `P1 (Alta)` | **Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Requisitos Atendidos:** Passo 06 do Escopo N1, Critério C3 (20%).
* **Descrição Detalhada:**
  1. Redigir `README.md` v1 oficial: visão geral, escopo entregue na N1, requisitos RF/RNF, galeria de capturas de tela das interfaces, guia de execução local em Python (`venv`, `pip install`, `uvicorn`) e link do sistema hospedado.
* **Branch:** `docs/n1-doc-02-readme-v1`
* **Pull Request:** Título `docs: [N1-DOC-02] Elaboração do README v1 oficial da fase N1` | Revisor: Gabriel Koehler da Silva.

---

### 🔹 Passo 08: Publicar o Sistema em Serviço de Hospedagem Gratuito

#### 📌 [N1-INF-01] Configuração de Hospedagem Contínua Gratuita (Render / Vercel)
* **Prioridade:** `P0 (Crítica)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Passo 08 do Escopo N1, Critério C2 (20%).
* **Descrição Detalhada:**
  1. Configurar pipeline de deploy contínuo em nuvem gratuita para a aplicação Python/FastAPI.
  2. Validar acesso público via HTTPS e registrar a URL pública no repositório.
* **Branch:** `infra/n1-inf-01-deploy-hospedagem`
* **Pull Request:** Título `infra: [N1-INF-01] Pipeline de deploy contínuo na nuvem N1` | Revisor: Gabriel Koehler da Silva.

---

### 🔹 Passo 09: Pacote de Entrega no Fim da Fase N1

#### 📌 [N1-INF-02] Automação do Pacote C1 (.zip limpo) e Auditoria Final N1
* **Prioridade:** `P0 (Crítica / Fechamento)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Passo 09 do Escopo N1, Critério C1 (10%).
* **Descrição Detalhada:**
  1. Criar script `scripts/package_delivery.py` para compactar o projeto em `.zip` excluindo pastas desnecessárias (`venv/`, `__pycache__/`, `.git/`, `node_modules/`).
  2. Auditar repositório garantindo zero PRs abertos.
* **Branch:** `infra/n1-inf-02-script-empacotamento-c1`
* **Pull Request:** Título `infra: [N1-INF-02] Script de empacotamento .zip C1 e auditoria final de PRs N1` | Revisor: Alyson de Lima de Oliveira.

---

# 📦 FASE 02 — N2: Integração Real com Supabase (PostgreSQL)

### 🔹 Passo 01: Conectar a Banco de Dados Real (Supabase) e Camadas sem Mock

#### 📌 [N2-BE-01] Implementação da Arquitetura em Camadas em Python
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RNF08, RNF09, Passo 01 da N2.
* **Descrição Detalhada:** Reorganizar backend Python nas camadas clássicas: `app/controllers/` (rotas HTTP), `app/services/` (regras e cálculos), `app/repositories/` (queries SQL) e `app/models/` (entidades).
* **Branch:** `feat/n2-be-01-arquitetura-camadas-python`
* **Pull Request:** Título `feat(back): [N2-BE-01] Estruturação da arquitetura em camadas em Python` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N2-BE-02] Configuração do Conector Supabase e Pool de Conexões
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RNF08, Passo 01 da N2.
* **Descrição Detalhada:** Configurar cliente Supabase (`supabase-py`) e pool PostgreSQL (`DATABASE_URL`). Implementar script de teste de conectividade e migração `app/database/migrate.py`.
* **Branch:** `feat/n2-be-02-supabase-client-pool`
* **Pull Request:** Título `feat(back): [N2-BE-02] Conexão pool com Supabase (PostgreSQL) e rotina de teste` | Revisor: Diego Rafael da Silva Dornelles.

#### 📌 [N2-BE-03] Implementação dos Repositories e Services CRUD sobre o Supabase
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF01 a RF13.
* **Descrição Detalhada:** Implementar Repositories e Services CRUD para Professores, Semestres, Turmas, Alunos e Questões/Alternativas sobre o Supabase, eliminando dados mock do backend.
* **Branch:** `feat/n2-be-03-crud-repositories-supabase`
* **Pull Request:** Título `feat(back): [N2-BE-03] Repositories e Services de cadastros básicos sobre Supabase` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N2-FE-01] Conexão Real da Autenticação e Semestres/Turmas com a API
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF01, RF02, RF03, Critério C2 da N2.
* **Descrição Detalhada:** Conectar formulários de login, semestres e turmas aos endpoints REST da API Python integrada ao Supabase com tratamento visual de erros.
* **Branch:** `feat/n2-fe-01-integracao-auth-turmas`
* **Pull Request:** Título `feat(front): [N2-FE-01] Conecta telas de autenticação e turmas ao backend com Supabase` | Revisor: Luan Eliseu.

#### 📌 [N2-FE-02] Conexão Real do Banco de Questões e Upload de Arquivos
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF06 a RF13, Critério C2 da N2.
* **Descrição Detalhada:** Conectar CRUD de questões e upload de planilhas à API real com gravação direta no Supabase.
* **Branch:** `feat/n2-fe-02-integracao-questoes-upload`
* **Pull Request:** Título `feat(front): [N2-FE-02] Integração real do CRUD de questões e importação em lote` | Revisor: Luan Eliseu.

#### 📌 [N2-BE-04] Persistência Transacional de Avaliações, Versões e Gabaritos no Supabase
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF14 a RF25, RN06, RN07, RN14.
* **Descrição Detalhada:** Método transacional em Python: grava avaliação, gera versões com embaralhamento e insere atomicamente em `versao_avaliacao`, `questao_versao` e `gabarito_versao`.
* **Branch:** `feat/n2-be-04-transacoes-avaliacoes-versoes`
* **Pull Request:** Título `feat(back): [N2-BE-04] Persistência transacional de avaliações, versões e gabaritos no Supabase` | Revisor: Alyson de Lima de Oliveira.

#### 📌 [N2-FE-03] Conexão da Criação de Avaliações e Persistência de Versões
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF14 a RF25, Critério C2 da N2.
* **Descrição Detalhada:** Conectar assistente de avaliações para buscar questões e enviar configurações de versões para a API Python, renderizando versões salvas no banco com QR Codes dinâmicos.
* **Branch:** `feat/n2-fe-03-integracao-avaliacoes-versoes`
* **Pull Request:** Título `feat(front): [N2-FE-03] Integração da criação e geração de versões com o banco real` | Revisor: Diego Rafael da Silva Dornelles.

#### 📌 [N2-BE-05] Módulo de Processamento de Imagem OMR (OpenCV) e Leitura de QR Code
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF31 a RF37, RF40.
* **Descrição Detalhada:** Serviço `app/services/omr_service.py` com OpenCV e pyzbar: decodificar QR Code da imagem da folha, segmentar alternativas e detectar bolinhas marcadas com validação de rasuras.
* **Branch:** `feat/n2-be-05-python-opencv-omr`
* **Pull Request:** Título `feat(back): [N2-BE-05] Módulo de Visão Computacional (OpenCV/pyzbar) para correção OMR` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N2-BE-06] Cálculo de Notas, Persistência no Supabase e Exportação Excel
* **Prioridade:** `P0 (Crítica)` | **Responsável:** Luan Eliseu
* **Requisitos Atendidos:** RF38, RF39, RF44 a RF48.
* **Descrição Detalhada:** Comparar respostas detectadas com `gabarito_versao`, calcular nota, persistir resultado no Supabase e gerar download de planilha formatada em Excel (`.xlsx`).
* **Branch:** `feat/n2-be-06-calculo-notas-exportacao-excel`
* **Pull Request:** Título `feat(back): [N2-BE-06] Cálculo de notas, persistência de correção no Supabase e exportação Excel` | Revisor: Gabriel Koehler da Silva.

#### 📌 [N2-FE-04] Interface de Correção Real e Download de Relatório Excel
* **Prioridade:** `P1 (Alta)` | **Responsável:** Gabriel Koehler da Silva
* **Requisitos Atendidos:** RF31, RF41 a RF48, Critério C2 da N2.
* **Descrição Detalhada:** Conectar tela de correção para envio da imagem ao endpoint OMR via multipart. Exibir nota calculada, estatísticas da turma e habilitar download do relatório Excel oficial.
* **Branch:** `feat/n2-fe-04-integracao-correcao-excel`
* **Pull Request:** Título `feat(front): [N2-FE-04] Integração da correção OMR real e download de relatório Excel` | Revisor: Luan Eliseu.

---

### 🔹 Passo 02: Modelar o Banco de Dados (MER/DER) e Documentar Decisões de Arquitetura

#### 📌 [N2-MER-01] Elaboração do Modelo Entidade-Relacionamento Conceitual (MER)
* **Prioridade:** `P0 (Crítica)` | **Responsável:** ELOISA FAZZIO DA SILVA ROCHA
* **Requisitos Atendidos:** Passo 02 e Critério C3 da N2.
* **Descrição Detalhada:** Desenvolver o MER conceitual em `docs/banco-de-dados/mer-conceitual.md` com entidades e cardinalidades completas.
* **Branch:** `docs/n2-mer-01-diagrama-mer-conceitual`
* **Pull Request:** Título `docs: [N2-MER-01] Elaboração do modelo entidade-relacionamento (MER) conceitual` | Revisor: Luan Eliseu.

#### 📌 [N2-MER-02] Dicionário de Dados e Regras de Integridade para Supabase
* **Prioridade:** `P1 (Alta)` | **Responsável:** ELOISA FAZZIO DA SILVA ROCHA
* **Requisitos Atendidos:** Passo 02 e Critério C3 da N2.
* **Descrição Detalhada:** Documentar em `docs/banco-de-dados/dicionario-de-dados.md` todas as tabelas, colunas, tipos PostgreSQL/Supabase, constraints e regras de integridade referencial.
* **Branch:** `docs/n2-mer-02-dicionario-dados-integridade`
* **Pull Request:** Título `docs: [N2-MER-02] Dicionário de dados completo e regras de integridade para Supabase` | Revisor: Alyson de Lima de Oliveira.

#### 📌 [N2-INF-01] Provisionamento do Projeto no Supabase, DER Físico e Scripts DDL
* **Prioridade:** `P0 (Crítica)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Passo 02 e Critério C3 da N2.
* **Descrição Detalhada:** Criar projeto no Supabase, documentar `.env.example`, elaborar DER físico e escrever scripts SQL PostgreSQL `src/database/schema.sql` e `src/database/seed.sql`. Executar no Supabase.
* **Branch:** `infra/n2-inf-01-supabase-der-ddl-seed`
* **Pull Request:** Título `infra: [N2-INF-01] Provisionamento do Supabase, DER físico e scripts DDL (schema) e Seed` | Revisor: Luan Eliseu.

#### 📌 [N2-DOC-01] Documentação da Arquitetura em Camadas e Decisões Técnicas (ADRs)
* **Prioridade:** `P1 (Alta)` | **Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Requisitos Atendidos:** Passo 02 e Critério C3 (20% da N2).
* **Descrição Detalhada:** Documentar `docs/arquitetura/arquitetura-em-camadas.md` e registrar ADRs fundamentando a escolha do Python/OpenCV e do Supabase.
* **Branch:** `docs/n2-doc-01-arquitetura-camadas-adr`
* **Pull Request:** Título `docs: [N2-DOC-01] Documentação da arquitetura em camadas e registros de decisão (ADRs)` | Revisor: Luan Eliseu.

---

### 🔹 Passo 03: Ampliar/Ajustar as Classes de Domínio e as Issues

#### 📌 [N2-INF-02] Elaboração do Diagrama de Classes UML v2 Atualizado
* **Prioridade:** `P1 (Alta)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Critério C3 (20% da N2), Passo 03 da N2.
* **Descrição Detalhada:** Elaborar Diagrama de Classes UML v2 em `docs/arquitetura/diagrama-classes-uml-v2.md` refletindo as classes Python e entidades Supabase implementadas.
* **Branch:** `docs/n2-inf-02-diagrama-classes-uml-v2`
* **Pull Request:** Título `docs: [N2-INF-02] Diagrama de classes UML v2 em conformidade com o código Python` | Revisor: Alyson de Lima de Oliveira.

---

### 🔹 Passo 05: Atualizar o README para a Versão v2

#### 📌 [N2-DOC-02] Atualização Oficial do README para a Versão v2 (Critério C3)
* **Prioridade:** `P1 (Alta)` | **Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Requisitos Atendidos:** Critério C3 (20% da N2), Passo 05.
* **Descrição Detalhada:** Atualizar `README.md` para v2 oficial com arquitetura em camadas, backend Python com OpenCV/OMR, banco Supabase, diagramas MER, DER e UML v2, variáveis `.env` e link de produção.
* **Branch:** `docs/n2-doc-02-readme-v2`
* **Pull Request:** Título `docs: [N2-DOC-02] Atualização do README oficial para versão v2 da N2 com Supabase` | Revisor: Gabriel Koehler da Silva.

---

### 🔹 Passo 07: Republicar o Sistema Hospedado Conectado ao Supabase

#### 📌 [N2-INF-03] Configuração de Produção do Supabase e Atualização do Deploy
* **Prioridade:** `P0 (Crítica)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Critério C2 (40% da N2), Passo 07.
* **Descrição Detalhada:** Configurar variáveis do Supabase no provedor de nuvem e certificar que a aplicação em produção opera 100% sobre o banco real, sem dados mock residuais.
* **Branch:** `infra/n2-inf-03-supabase-cloud-deploy-n2`
* **Pull Request:** Título `infra: [N2-INF-03] Configuração de produção com Supabase e republicação do sistema N2` | Revisor: Gabriel Koehler da Silva.

---

### 🔹 Passo 08: Entrega no Fim da Fase N2 (Código Zipado, Docs v2 e Link no Ar)

#### 📌 [N2-INF-04] Pacote de Entrega C1 (.zip) e Homologação Final N2
* **Prioridade:** `P0 (Crítica / Fechamento)` | **Responsável:** DIEGO RAFAEL DA SILVA DORNELLES
* **Requisitos Atendidos:** Critério C1 (10% da N2), Passo 08.
* **Descrição Detalhada:** Gerar arquivo `.zip` limpo da fase N2, testar descompactação e validar conformidade com os critérios C1, C2 e C3.
* **Branch:** `infra/n2-inf-04-pacote-entrega-n2`
* **Pull Request:** Título `infra: [N2-INF-04] Pacote .zip C1 e homologação final N2` | Revisor: Alyson de Lima de Oliveira.
