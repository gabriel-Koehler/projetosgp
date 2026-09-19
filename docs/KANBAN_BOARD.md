# 📋 QUADRO KANBAN OFICIAL: ETAPAS N1 E N2 (ESCOPO E CRITÉRIOS DE AVALIAÇÃO)

Este quadro organiza todas as atividades do projeto no GitHub pelas **Etapas / Passos oficiais do arquivo "Escopo do Projeto e Critérios de Avaliação"**, cobrindo **exclusivamente as Fases N1 e N2**.

---

## 👥 Matriz de Responsabilidades da Equipe
* 🎨 **Front-end & Mocks/Setup:** Gabriel Koehler da Silva
* ⚙️ **Back-end & Banco de Dados:** Luan Eliseu (Python FastAPI + Supabase + OpenCV/OMR)
* 📄 **Documentação & Arquitetura:** ALYSON DE LIMA DE OLIVEIRA
* 📐 **Requisitos & Testes:** ELOISA FAZZIO DA SILVA ROCHA
* 🚀 **Infraestrutura, Deploy & DER:** DIEGO RAFAEL DA SILVA DORNELLES

---

## 🔄 Ciclo Obrigatório de Entrega de Toda Atividade
> **Regra do Projeto:** Commits semânticos, Pull Request, Revisão de Código e Merge compõem a **etapa obrigatória de conclusão de todo e qualquer card executado**:
```
[ 🌿 Branch própria ] ➔ [ 💻 Commits com ID do Card ] ➔ [ 🔍 Abertura de PR contra main ] ➔ [ 👥 Code Review do colega ] ➔ [ ✅ Merge na main ]
```

---

# 📦 FASE 01 — N1: Telas Navegáveis (Dados Mock)

| Etapa do Documento Oficial | ID Card | Título da Atividade | Responsável | Prioridade | Branch Padronizada | Revisor do PR |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| **Passo 02: Briefing & Classes de Domínio** | **N1-DOC-01** | Esboço Inicial das Classes de Domínio | Alyson de Lima | `P0` | `docs/n1-doc-01-classes-dominio` | Eloisa Fazzio |
| **Passo 02: Briefing & Classes de Domínio** | **N1-REQ-01** | Mapeamento de Fluxos e Casos de Uso | Eloisa Fazzio | `P0` | `docs/n1-req-01-fluxos-casos-uso` | Gabriel Koehler |
| **Passo 03: Repositório GitHub & Issues** | **N1-INF-03** | Setup Repositório, Labels e Kanban Board | Gabriel Koehler | `P0` | `infra/n1-inf-03-setup-repo-kanban` | Alyson de Lima |
| **Passo 04: Telas Navegáveis com Mock** | **N1-BE-01** | Setup API Python (FastAPI) e Sessão | Luan Eliseu | `P0` | `feat/n1-be-01-setup-api-python-auth` | Gabriel Koehler |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-01** | Layout Base, Design System e Login | Gabriel Koehler | `P0` | `feat/n1-fe-01-layout-login` | Luan Eliseu |
| **Passo 04: Telas Navegáveis com Mock** | **N1-BE-02** | Provedor de Dados Mock State em Python | Gabriel Koehler | `P1` | `feat/n1-be-02-python-mock-state` | Luan Eliseu |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-02** | Semestres e Turmas Navegáveis | Gabriel Koehler | `P1` | `feat/n1-fe-02-semestres-turmas` | Eloisa Fazzio |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-03** | Alunos e Importação CSV/Excel | Gabriel Koehler | `P1` | `feat/n1-fe-03-alunos-importacao` | Diego Rafael |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-04** | Banco de Questões (CRUD e Importação) | Gabriel Koehler | `P1` | `feat/n1-fe-04-banco-questoes` | Luan Eliseu |
| **Passo 04: Telas Navegáveis com Mock** | **N1-BE-03** | Core Python: Embaralhamento e Gabaritos | Luan Eliseu | `P0` | `feat/n1-be-03-python-core-embaralhamento` | Gabriel Koehler |
| **Passo 04: Telas Navegáveis com Mock** | **N1-BE-04** | Geração de QR Code e Rota Aluno Python | Luan Eliseu | `P1` | `feat/n1-be-04-python-qrcode-aluno` | Alyson de Lima |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-05** | Assistente de Criação de Avaliações/Versões | Gabriel Koehler | `P0` | `feat/n1-fe-05-criacao-avaliacoes-versoes` | Alyson de Lima |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-06** | Impressão de Provas, Folha e Tela Aluno | Gabriel Koehler | `P1` | `feat/n1-fe-06-impressao-prova-aluno` | Eloisa Fazzio |
| **Passo 04: Telas Navegáveis com Mock** | **N1-FE-07** | Simulação de Correção e Estatísticas | Gabriel Koehler | `P1` | `feat/n1-fe-07-correcao-estatisticas` | Luan Eliseu |
| **Passo 04: Telas Navegáveis com Mock** | **N1-REQ-02** | Roteiro e Execução de Testes Navegáveis N1 | Eloisa Fazzio | `P1` | `test/n1-req-02-testes-aceitacao-navegavel` | Luan Eliseu |
| **Passo 06: README v1 (modelo_doc.md)** | **N1-DOC-02** | Elaboração do README v1 Oficial (C3) | Alyson de Lima | `P1` | `docs/n1-doc-02-readme-v1` | Gabriel Koehler |
| **Passo 08: Hospedagem Gratuita (C2 - 20%)** | **N1-INF-01** | Deploy Contínuo em Nuvem (Render / Vercel) | Diego Rafael | `P0` | `infra/n1-inf-01-deploy-hospedagem` | Gabriel Koehler |
| **Passo 09: Pacote de Entrega N1 (C1 - 10%)** | **N1-INF-02** | Script Empacotamento .zip C1 e Auditoria | Diego Rafael | `P0` | `infra/n1-inf-02-script-empacotamento-c1` | Alyson de Lima |

---

# 📦 FASE 02 — N2: Integração Real com Supabase (PostgreSQL)

| Etapa do Documento Oficial | ID Card | Título da Atividade | Responsável | Prioridade | Branch Padronizada | Revisor do PR |
| :--- | :---: | :--- | :--- | :---: | :--- | :--- |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-01** | Camadas em Python (Controller/Service/Repo) | Luan Eliseu | `P0` | `feat/n2-be-01-arquitetura-camadas-python` | Gabriel Koehler |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-02** | Conector Supabase e Pool PostgreSQL | Luan Eliseu | `P0` | `feat/n2-be-02-supabase-client-pool` | Diego Rafael |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-03** | CRUDs no Supabase (Turmas e Questões) | Luan Eliseu | `P0` | `feat/n2-be-03-crud-repositories-supabase` | Gabriel Koehler |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-FE-01** | Conecta Auth e Turmas ao Supabase | Gabriel Koehler | `P1` | `feat/n2-fe-01-integracao-auth-turmas` | Luan Eliseu |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-FE-02** | Conecta Banco de Questões e Upload | Gabriel Koehler | `P1` | `feat/n2-fe-02-integracao-questoes-upload` | Luan Eliseu |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-04** | Persistência Transacional de Versões | Luan Eliseu | `P0` | `feat/n2-be-04-transacoes-avaliacoes-versoes` | Alyson de Lima |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-FE-03** | Conecta Criação de Avaliações ao Banco | Gabriel Koehler | `P1` | `feat/n2-fe-03-integracao-avaliacoes-versoes` | Diego Rafael |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-05** | Módulo OMR Python (OpenCV/pyzbar) | Luan Eliseu | `P0` | `feat/n2-be-05-python-opencv-omr` | Gabriel Koehler |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-BE-06** | Cálculo de Notas e Exportação Excel | Luan Eliseu | `P0` | `feat/n2-be-06-calculo-notas-exportacao-excel` | Gabriel Koehler |
| **Passo 01: Banco Real & Camadas sem Mock** | **N2-FE-04** | Interface Correção Real e Download Excel | Gabriel Koehler | `P1` | `feat/n2-fe-04-integracao-correcao-excel` | Luan Eliseu |
| **Passo 02: Modelar Banco & Decisões (ADRs)** | **N2-MER-01** | Modelo MER Conceitual e Cardinalidades | Eloisa Fazzio | `P0` | `docs/n2-mer-01-diagrama-mer-conceitual` | Luan Eliseu |
| **Passo 02: Modelar Banco & Decisões (ADRs)** | **N2-MER-02** | Dicionário de Dados para Supabase | Eloisa Fazzio | `P1` | `docs/n2-mer-02-dicionario-dados-integridade` | Alyson de Lima |
| **Passo 02: Modelar Banco & Decisões (ADRs)** | **N2-INF-01** | Supabase DER e Scripts DDL (`schema.sql`) | Diego Rafael | `P0` | `infra/n2-inf-01-supabase-der-ddl-seed` | Luan Eliseu |
| **Passo 02: Modelar Banco & Decisões (ADRs)** | **N2-DOC-01** | Documentação das Camadas e ADRs | Alyson de Lima | `P1` | `docs/n2-doc-01-arquitetura-camadas-adr` | Luan Eliseu |
| **Passo 03: Classes de Domínio e UML v2** | **N2-INF-02** | Diagrama de Classes UML v2 Atualizado | Diego Rafael | `P1` | `docs/n2-inf-02-diagrama-classes-uml-v2` | Alyson de Lima |
| **Passo 05: Atualização do README para v2** | **N2-DOC-02** | README v2 Oficial com Supabase (C3 - 20%) | Alyson de Lima | `P1` | `docs/n2-doc-02-readme-v2` | Gabriel Koehler |
| **Passo 07: Republicar Sistema (C2 - 40%)** | **N2-INF-03** | Deploy do Sistema com Supabase em Produção | Diego Rafael | `P0` | `infra/n2-inf-03-supabase-cloud-deploy-n2` | Gabriel Koehler |
| **Passo 08: Entrega N2 (.zip C1 10%)** | **N2-INF-04** | Pacote .zip C1 e Homologação Final N2 | Diego Rafael | `P0` | `infra/n2-inf-04-pacote-entrega-n2` | Alyson de Lima |
