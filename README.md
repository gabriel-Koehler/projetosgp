# 🎓 Sistema de Geração e Correção Automática de Avaliações

> Repositório oficial para desenvolvimento do projeto da disciplina de **Projeto e Arquitetura de Software** (Fases **N1** e **N2**).

---

## 👥 Equipe e Responsabilidades Oficiais

| Integrante | Atribuição | Responsabilidades |
| :--- | :--- | :--- |
| **Gabriel Koehler da Silva** | **Front-end & Mocks/Setup** | Desenvolvimento de todas as interfaces web navegáveis (N1), usabilidade, responsividade, integração com a API REST Python e telas de correção/relatórios (N2), além da estruturação do repositório/Kanban (`[N1-INF-03]`) e do provedor mock state (`[N1-BE-02]`). |
| **Luan Eliseu** | **Back-end & Banco de Dados** | Desenvolvimento da API em Python (FastAPI), módulo de Visão Computacional / OMR via OpenCV (`cv2`) e pyzbar, integração com Supabase (`supabase-py`), regras de embaralhamento e gabaritos, CRUDs relacionais e exportação Excel. |
| **ALYSON DE LIMA DE OLIVEIRA** | **Documentação & Arquitetura** | Esboço inicial das classes de domínio, elaboração dos READMEs oficiais (v1 e v2) e documentação formal da arquitetura em camadas e registros de decisões técnicas (ADRs). |
| **ELOISA FAZZIO DA SILVA ROCHA** | **Requisitos, Fluxos & Modelagem Conceitual** | Mapeamento de fluxos de navegação e casos de uso, roteiro de testes navegáveis de aceitação (N1), Modelagem Conceitual (MER) e Dicionário de Dados para o Supabase (N2). |
| **DIEGO RAFAEL DA SILVA DORNELLES** | **Infraestrutura, Deploy & Modelagem Física** | Configuração de deploy contínuo em nuvem (Render/Vercel), automação do pacote de entrega C1 (.zip), provisionamento do Supabase, DER Físico, scripts DDL/Seed (`schema.sql`) e Diagrama UML v2. |

---

## 🏛️ Arquitetura e Tecnologias

* **Front-end:** HTML5 semântico, CSS3 responsivo (com `@media print` para provas e folhas de resposta) e JavaScript modular.
* **Back-end:** **Python 3.11** com **FastAPI** para alta performance e suporte nativo assíncrono.
* **Visão Computacional / OMR:** **OpenCV (`cv2`)**, **pyzbar** e **NumPy** para decodificação de QR Code na folha de respostas, segmentação de bolinhas e correção automática das alternativas assinaladas.
* **Banco de Dados:** **Supabase (PostgreSQL Cloud)** com pooling de conexões e **Supabase Storage** para armazenamento das fotos/scans das folhas de resposta.

---

## 🌐 Acesso ao Sistema em Nuvem (Critério C2)

A aplicação está publicada e acessível no seguinte endereço:
* **Ambiente Online:** [https://projetosgp-e9dz.vercel.app/](https://projetosgp-e9dz.vercel.app/)

### 🔑 Credenciais de Demonstração (Acesso Docente)
* **E-mail / Usuário:** `professor@avaliasystem.com` *(ou `professor`)*
* **Senha:** `123456`

> ℹ️ **Nota de Interface:** O botão *"Continuar com o Google"* é um elemento visual demonstrativo de MVP; para autenticar e testar todas as funcionalidades, utilize as credenciais de demonstração acima.

### 👨‍🎓 Acesso do Aluno
Conforme a regra de negócio do projeto (RN02), o estudante **não possui login nem painel administrativo**. O acesso do aluno é público e restrito à conferência do gabarito da sua versão da prova através da leitura do QR Code impresso na avaliação ou pela rota `/student`.

---

## 📖 Como Usar o Sistema (Guia de Navegação)

O fluxo operacional do **AvaliaSystem** segue a jornada do professor documentada em [`docs/requisitos/fluxos-de-usuario.md`](docs/requisitos/fluxos-de-usuario.md):

### 1. Autenticação e Painel Principal
1. Acesse a tela de login (`/`) e informe as credenciais de demonstração.
2. No **Painel do Professor (`DashboardScreen`)**, visualize as métricas gerais (questões no banco, provas corrigidas, avaliações criadas e alunos ativos), o gráfico de correções e os atalhos rápidos (*Corrigir prova*, *Nova avaliação* e *Ver resultados*).

### 2. Gestão de Semestres, Turmas e Alunos
1. No menu lateral fixo, clique em **Semestres & Turmas** (`SemestresScreen`).
2. Selecione o período letivo desejado na lista lateral esquerda.
3. Na aba **Turmas**, visualize as turmas cadastradas ou clique em **"+ Nova turma"** para registrar uma turma vinculada ao semestre.
4. Na aba **Alunos**, visualize a lista de estudantes ou utilize o botão **"Importar alunos"** para carregar arquivos `.csv` ou `.xlsx` com prévia e confirmação.

### 3. Banco de Questões
1. No menu lateral, acesse **Banco de Questões** (`BancoQuestoesScreen`).
2. Utilize os filtros laterais por disciplina, nível de dificuldade (Fácil, Média, Difícil) ou a barra de pesquisa textual.
3. Clique em **"Nova questão"** para cadastrar enunciados, alternativas e definir a resposta correta, ou em **"Importar"** para carga em lote via planilha modelo.

### 4. Elaboração de Avaliações em 4 Passos
No menu ou no painel, clique em **"Nova avaliação"** para iniciar o assistente (`CriarAvaliacaoScreen`):
* **Passo 1 (Configurar):** Preencha nome da prova, semestre letivo, turma de destino, data de aplicação e instruções gerais.
* **Passo 2 (Questões):** Selecione as questões do banco que comporão a prova, acompanhando o contador no painel lateral fixo.
* **Passo 3 (Gabarito):** Confira ou personalize a alternativa correta de cada questão selecionada para a prova.
* **Passo 4 (Versões):** Defina a quantidade de versões (ex.: A, B, C) e habilite o embaralhamento de questões e de alternativas para mitigar cola. Ao finalizar, clique em **"Gerar avaliação"**.

### 5. Versões, Impressão e QR Code
1. Na tela **Versões & QR Code** (`VersoesScreen`), alterne entre as versões geradas (A, B, C) para inspecionar as questões e os gabaritos correspondentes.
2. Baixe o **QR Code** exclusivo de cada versão em `.png`.
3. Gere e imprima os documentos diagramados para folha A4 com `@media print`: a **Prova do Aluno**, a **Folha de Respostas OMR** (com marcadores de canto e grade de bolhas) e o **Gabarito Docente**.

### 6. Correção e Resultados
1. No menu lateral ou painel, clique em **Correção Automática**: envie a imagem da folha de respostas preenchida para decodificação do QR Code e leitura óptica ou utilize a conferência manual das respostas.
2. Acesse a tela de **Resultados**: consulte as notas apuradas por aluno, verifique as estatísticas de desempenho por questão e exporte a planilha consolidada para Excel (`.xlsx`).

---


## 📋 Organização do Trabalho e Governança no GitHub

O projeto é organizado rigorosamente pelas etapas do documento oficial **Escopo do Projeto e Critérios de Avaliação**:
* 📊 **Quadro Kanban Oficial:** Consulte o arquivo [`docs/KANBAN_BOARD.md`](docs/KANBAN_BOARD.md) para visualizar todas as 32 atividades organizadas por etapas.
* 📝 **Backlog Detalhado:** Consulte [`docs/PROJECT_BACKLOG.md`](docs/PROJECT_BACKLOG.md) para ver a descrição detalhada, requisitos e critérios de aceite de cada card.
* 🌿 **Fluxo de Trabalho Obrigatório:**
  ```
  [ Branch própria a partir da main ] ➔ [ Commits Semânticos ] ➔ [ Pull Request (PR) ] ➔ [ Code Review Cruzado ] ➔ [ Merge na main ]
  ```

---

## ⚙️ Automação de Issues e Labels no GitHub

O repositório possui um script em Python para criar automaticamente todas as labels e as 32 issues diretamente no GitHub:

```bash
python scripts/create_github_issues_kanban.py SEU_TOKEN_GITHUB_AQUI
```

---

## 📦 Estrutura de Diretórios do Repositório

```
.
├── .github/
│   └── ISSUE_TEMPLATE/
│       └── card-atividade.md       # Template oficial para criação de issues
├── docs/
│   ├── KANBAN_BOARD.md             # Quadro Kanban das Etapas N1 e N2
│   └── PROJECT_BACKLOG.md          # Backlog técnico com os 32 cards detalhados
├── scripts/
│   └── create_github_issues_kanban.py  # Script de automação de issues e labels
├── public/                         # Arquivos estáticos (CSS, imagens)
├── app/                            # Backend em Python (FastAPI)
└── README.md                       # Documentação principal
```