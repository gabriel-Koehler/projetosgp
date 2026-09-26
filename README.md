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
## MVP AvaliaSystem

Instruções de execução, conta demo, escopo e validação: [N1-FE-01](docs/N1-FE-01.md).
