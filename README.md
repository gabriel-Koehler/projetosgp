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

## ⚙️ Back-end (API Python)

### Como rodar localmente

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
copy .env.example .env            # Linux/macOS: cp .env.example .env  (ajuste os valores)
uvicorn app.main:app --reload
```

* API em `http://localhost:8000` e documentação interativa das rotas em `http://localhost:8000/docs`.
* Testes: `pytest`. Os testes de banco só rodam com `TEST_DATABASE_URL` apontando para um PostgreSQL **descartável** (as tabelas são apagadas e recriadas); sem ela, são pulados.

### Banco de dados (Supabase)

1. No Supabase, copie a connection string em *Project Settings → Database* e coloque em `DATABASE_URL` no `.env`.
2. Crie as tabelas e o professor inicial: `python -m app.database.migrate` (pode rodar de novo sem problema).
3. Teste a conexão: `python -m app.database.check` (lista tabelas faltando e confere o bucket do Storage).
4. `GET /api/health` responde `"banco": "ok"` quando a API está conectada.

* O esquema fica em [`app/database/schema.sql`](app/database/schema.sql).
* Os dados são acessados direto pelo PostgreSQL (`psycopg` com pool de conexões), porque a API REST do Supabase não faz transações com vários comandos. O `supabase-py` é usado para o **Storage** das fotos das folhas de resposta.
* Login padrão da N1 (mock): usuário `professor`, senha `123456` (configurável no `.env`).

### Variáveis de ambiente (`.env`)

| Variável | Para que serve |
| :--- | :--- |
| `SECRET_KEY` | Assina o cookie de sessão. **Obrigatória em produção** (sem ela, todo reinício desloga o professor). |
| `PROFESSOR_USERNAME` / `PROFESSOR_PASSWORD` / `PROFESSOR_NOME` | Credenciais do professor na N1. Na N2 passam a vir do Supabase. |
| `SESSION_HTTPS_ONLY` | `true` em produção: o cookie só trafega por HTTPS. |
| `DATABASE_URL` | Connection string do PostgreSQL do Supabase. Em produção, use o pooler (porta 6543). |
| `SUPABASE_URL` / `SUPABASE_KEY` / `SUPABASE_BUCKET` | Supabase Storage para guardar as fotos das folhas corrigidas (opcional). |
| `CORS_ORIGINS` | Origens do front autorizadas, separadas por vírgula. Vazio se o front for servido pelo mesmo domínio. |
| `PUBLIC_BASE_URL` | Domínio público usado no link do QR Code (ex.: `https://provafacil.onrender.com`). Vazio = endereço da requisição. |

### Rotas disponíveis

| Método | Rota | Login | O que faz |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/health` | — | Verificação para o deploy. |
| `POST` | `/api/auth/login` | — | Corpo `{"username", "password"}`. Cria a sessão; `401` se inválido. |
| `POST` | `/api/auth/logout` | — | Encerra a sessão. |
| `GET` | `/api/auth/me` | ✅ | Professor logado (`username`, `nome`) — use para mostrar o nome na navbar. |
| `GET` / `POST` | `/api/semestres` | ✅ | Lista (`?ativo=true`) / cadastra semestres (RF02). |
| `GET` / `PUT` | `/api/semestres/{id}` | ✅ | Consulta / edita um semestre. |
| `PATCH` | `/api/semestres/{id}/ativo` | ✅ | Corpo `{"ativo": false}` desativa (ou reativa) o semestre. |
| `GET` / `POST` | `/api/turmas` | ✅ | Lista (`?semestre_id=`) / cadastra turmas (RF03). |
| `GET` / `PUT` / `DELETE` | `/api/turmas/{id}` | ✅ | Consulta / edita / exclui (`409` se tiver alunos ou avaliações). |
| `GET` / `POST` | `/api/turmas/{id}/alunos` | ✅ | Lista / cadastra alunos da turma (RF04). |
| `POST` | `/api/turmas/{id}/alunos/importar` | ✅ | Importa planilha (campo `arquivo`, RF05). Ver "Importações" abaixo. |
| `GET` / `PUT` / `DELETE` | `/api/alunos/{id}` | ✅ | Consulta / edita / exclui um aluno. |
| `GET` | `/api/alunos/modelo.csv` e `.xlsx` | ✅ | Modelo de planilha de alunos. |
| `GET` / `POST` | `/api/questoes` | ✅ | Busca (`?busca=&disciplina=&categoria=&dificuldade=&pagina=&por_pagina=`) / cadastra questões (RF06, RF09). |
| `GET` / `PUT` / `DELETE` | `/api/questoes/{id}` | ✅ | Consulta / edita / exclui. Questão já usada em avaliação é **arquivada** em vez de apagada (RF08). |
| `GET` | `/api/questoes/filtros` | ✅ | Disciplinas e categorias já cadastradas (para os filtros da tela). |
| `POST` | `/api/questoes/importar` | ✅ | Importa planilha de questões (campo `arquivo`, RF10 a RF12). |
| `GET` | `/api/questoes/modelo.csv` e `.xlsx` | ✅ | Modelo de planilha de questões (RF13). |
| `POST` | `/api/avaliacoes` | ✅ | Cria a avaliação e gera as versões, gabaritos e códigos de QR Code. |
| `GET` | `/api/avaliacoes` | ✅ | Lista resumida (`?turma_id=`): nome, turma, quantidade de versões e de questões. |
| `GET` / `DELETE` | `/api/avaliacoes/{id}` | ✅ | Detalha com versões e gabaritos / exclui (`409` se já tiver provas corrigidas). |
| `PATCH` | `/api/avaliacoes/{id}/gabarito` | ✅ | Corpo `{"liberado": true}` libera (ou bloqueia) a consulta do gabarito pelo aluno. |
| `GET` | `/api/avaliacoes/{id}/versoes/{codigo}/qrcode.png` | ✅ | Imagem PNG do QR Code da versão, para a prova impressa. |
| `GET` | `/api/avaliacoes/{id}/versoes/{codigo}/folha.pdf` e `.png` | ✅ | Folha de respostas da versão (A4, com QR Code e marcadores) para imprimir (RF27). |
| `POST` | `/api/correcoes/leitura` | ✅ | Envia a foto da folha (campo `imagem`) e recebe as respostas lidas, **sem registrar** (RF31 a RF36). |
| `GET` | `/student/gabarito/{codigo}` | — | Rota pública do aluno (é o link dentro do QR Code). |

### Orientações para o front-end

**Autenticação.** O login usa **cookie de sessão** (`sessao_professor`), não token. Nas chamadas com `fetch`, envie `credentials: "include"`. Qualquer rota administrativa responde `401` sem login — redirecione para a tela de login.

> ⚠️ O cookie usa `SameSite=Lax`: front e API devem ficar **no mesmo domínio** (ex.: o FastAPI servindo as telas, ou um proxy). Se forem publicados em domínios diferentes (ex.: Vercel + Render), o navegador não envia o cookie — combinar com o back-end antes do deploy.

```js
await fetch("/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({ username, password }),
});
```

**Mensagens de erro.** Os erros vêm em `{"detail": "mensagem em português"}` e podem ser exibidos direto ao professor (ex.: `"Usuário ou senha inválidos."`, `"Informe exatamente 3 nome(s) de versão, sem nomes vazios."`).

**Questões.** Corpo do cadastro/edição: `{"enunciado", "alternativas": ["A", "B", "C", "D"] (E opcional), "correta": "B", "disciplina", "categoria", "dificuldade": "facil" | "media" | "dificil"}`.

**Importações (alunos e questões).** Envie o arquivo `.xlsx` ou `.csv` no campo `arquivo` (multipart). Fluxo em dois passos:
1. `POST .../importar` → **prévia**, nada é gravado: `{"total_linhas", "validas": [{"linha", "dados"}], "erros": [{"linha", "mensagens": [...]}], "importados": 0}`.
2. Professor confere e confirma → mesmo arquivo em `POST .../importar?confirmar=true` → grava só as linhas válidas e devolve `importados`.

Colunas das questões: `enunciado`, `alternativa_a` … `alternativa_d` (`alternativa_e` opcional), `gabarito`, `disciplina`, `categoria`, `dificuldade`. Colunas dos alunos: `nome`, `matricula`, `email`. Acentos e maiúsculas no cabeçalho são ignorados. Questões repetidas (na planilha ou já no banco) aparecem como erro.

**Criar avaliação.** O front envia os **ids das questões do banco**, na ordem da prova. Tudo (avaliação, versões, questões de cada versão e gabaritos) é gravado numa transação só: se algo falhar, nada fica salvo.

```json
{
  "nome": "N1 — Engenharia de Software",
  "turma_id": 3,
  "questao_ids": [12, 7, 30, 4],
  "gabaritos": { "7": "C" },
  "nota_maxima": 10,
  "configuracao": {
    "quantidade": 3,
    "nomenclatura": "letras",
    "nomes_personalizados": [],
    "mesmas_questoes": true,
    "questoes_por_versao": null,
    "embaralhar_questoes": true,
    "embaralhar_alternativas": true
  }
}
```

* `gabaritos` (opcional, RF16): ajusta a alternativa correta **só nesta avaliação**, sem mudar a questão no banco.
* `nomenclatura`: `letras` (A, B, C), `numeros` (1, 2, 3), `cores` (Azul, Verde, Amarela) ou `personalizada` (exige `nomes_personalizados` com um nome por versão).
* `mesmas_questoes: false` + `questoes_por_versao`: cada versão recebe um conjunto diferente de questões (sem repetição quando há questões suficientes).
* A resposta traz, para cada versão: `nome`, `codigo`, `url_aluno`, `url_qrcode`, `questoes` (já na ordem da versão, com a letra `correta`) e `gabarito` (`{"1": "C", "2": "A", ...}`).

**Prova impressa e folha de respostas.** Use a imagem de `url_qrcode` em um `<img src>` (a sessão do professor autentica a requisição, desde que front e API estejam no mesmo domínio). O mesmo QR Code será lido na correção automática (N2) para identificar a avaliação e a versão.

**Folha de respostas e correção automática (OMR).**
* A folha é **gerada pelo back-end** (`folha.pdf`), porque a leitura depende do layout exato: 4 quadrados pretos nos cantos, QR Code no alto à direita e grade de bolinhas. Imprima em **tamanho real (100%)**, sem "ajustar à página". Comporta até 93 questões de 2 a 5 alternativas.
* A foto pode ser tirada com o celular, torta, com sombra, deitada ou de cabeça para baixo — mas com os 4 cantos aparecendo.
* `POST /api/correcoes/leitura` responde `{"codigo", "avaliacao_id", "avaliacao", "versao", "confiavel", "mensagem", "respostas": {"1": "A", "2": null}, "em_branco", "multiplas", "ilegiveis", "questoes": [...]}`.
* `confiavel: false` = alguma marcação ficou duvidosa (rasura, marca fraca, "X"): mostrar `mensagem` e pedir nova foto ou conferência (RN15). Em branco e mais de uma marcação (anulada) não impedem o registro, só aparecem como aviso.
* Folha que não dá para ler responde `422` com `{"codigo", "detail"}`. Códigos: `imagem_invalida`, `folha_fora_do_padrao`, `qrcode_nao_lido`, `prova_desconhecida`.

**Tela do aluno.** `/student/gabarito/{codigo}` devolve **JSON**, sem login:

```json
{ "avaliacao": "N1 — Engenharia de Software", "versao": "A", "gabarito": [{ "questao": 1, "alternativa": "C" }] }
```

* O gabarito fica **bloqueado até o professor liberar** (`PATCH /api/avaliacoes/{id}/gabarito`): o QR Code está impresso na prova e, sem isso, o aluno veria as respostas durante a prova. Enquanto bloqueado, a rota responde `403` com a mensagem para exibir.
* Código inexistente responde `404`. A página visual do aluno é do card [N1-FE-06].

**Novas rotas administrativas.** Proteja o router inteiro com a dependência de login:

```python
from fastapi import APIRouter, Depends
from app.core.security import require_professor

router = APIRouter(prefix="/api/semestres", dependencies=[Depends(require_professor)])
```

Depois registre o router em `app/main.py` (`app.include_router(...)`).

**Camadas.** Cada funcionalidade segue `controllers/` → `services/` → `repositories/`: o controller só trata HTTP, o service aplica as regras e o repository fala com o banco. Erros de regra são lançados como `ErroDeNegocio` / `NaoEncontrado` / `AcessoNegado` / `Conflito` (`app/services/errors.py`) e viram respostas `422` / `404` / `403` / `409` com `{"detail": "..."}`.

---

## 🤝 Pontos a Combinar entre Back-end e Equipe

> Lista viva: quem resolver um item marca `[x]` e anota a decisão ao lado (ou o link da ADR/PR). Dúvidas sobre o back-end: **Luan Eliseu**.

### Decisões já tomadas no back-end (para todos seguirem)

* **Gabarito bloqueado até o professor liberar.** O QR Code vai impresso na prova; se a consulta ficasse aberta, o aluno veria as respostas durante a prova. O professor libera em `PATCH /api/avaliacoes/{id}/gabarito`.
* **QR Code com código aleatório por versão** (`/student/gabarito/{codigo}`), e não com o id sequencial: ninguém consegue adivinhar o link de outra versão. O código identifica a avaliação e a versão — é ele que a correção automática (OMR) vai ler.
* **Banco de dados: Supabase (PostgreSQL)**, decisão da equipe (o RNF08 do documento cita MySQL; justificativa vai em ADR).
* **Login por cookie de sessão** (`sessao_professor`, `SameSite=Lax`), não por token.
* **Gabarito calculado pela posição da alternativa**, nunca pelo texto (alternativas com texto repetido não quebram o gabarito). Cada questão da versão guarda `ordem_original`, que liga a alternativa exibida à letra original do banco — necessário para as estatísticas por alternativa.

### 🎨 Com o Gabriel (Front-end)

- [ ] **Quem serve as telas:** o FastAPI (templates Jinja2 + arquivos estáticos) ou um front separado? Como o login é por cookie `SameSite=Lax`, front e API precisam ficar **no mesmo domínio**. Recomendação do back-end: FastAPI servindo as telas.
- [ ] **Destino do código Node/Express** (`server.js`, `src/core.js`, `views/*.ejs`, `package.json`): migrar as telas para o FastAPI e remover o Node, ou manter só como protótipo até a migração?
- [ ] **`node_modules/` está versionado no git.** Adicionar ao `.gitignore` e remover do repositório.
- [ ] **[N1-BE-02] Provedor mock:** proteger `/api/semestres`, `/api/turmas`, `/api/questoes` com `Depends(require_professor)` (ver exemplo acima) e usar os mesmos campos de questão da API: `id`, `enunciado`, `alternativas` (lista), `correta` (letra).
- [ ] **Criação de avaliação (N2):** o front passa a enviar `questao_ids` (ids do banco de questões) e `turma_id`, em vez das questões completas. Ver exemplo acima.
- [ ] **[N1-FE-06] Tela do aluno:** consome o JSON de `/student/gabarito/{codigo}` e trata `403` (gabarito ainda não liberado) e `404` (QR Code inválido).
- [ ] **[N1-FE-05] Botão "Liberar gabarito"** na tela da avaliação, chamando o `PATCH /api/avaliacoes/{id}/gabarito`.
- [ ] **[N1-FE-06] Folha de respostas:** usar a folha gerada pelo back-end (`GET /api/avaliacoes/{id}/versoes/{codigo}/folha.pdf`) em vez de diagramar em HTML — a leitura automática depende do layout exato. O front só precisa de um botão "Imprimir folha de respostas" por versão. A prova com os enunciados continua sendo HTML (`@media print`).

### 🚀 Com o Diego (Infraestrutura e Deploy)

- [ ] **Deploy no mesmo domínio** para front e API (ver item do cookie acima). Se o front for para a Vercel e a API para o Render, avisar o back-end para ajustar a sessão.
- [ ] **Leitor de QR Code no servidor:** o `pyzbar` precisa da biblioteca do sistema `libzbar0`. Se o Render permitir (ex.: deploy com Docker, `apt-get install -y libzbar0`), instalar; se não, a API usa sozinha o leitor do OpenCV (um pouco menos tolerante a fotos ruins).
- [ ] **Comando de start no Render:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; build: `pip install -r requirements.txt`; health check: `/api/health`.
- [ ] **Variáveis de produção:** `SECRET_KEY` (valor aleatório e fixo), `SESSION_HTTPS_ONLY=true`, `PUBLIC_BASE_URL` (URL pública do sistema, usada no QR Code), `PROFESSOR_USERNAME`/`PROFESSOR_PASSWORD`.
- [ ] **Versão do Python:** o README cita 3.11; o back-end foi testado no 3.14. Fixar a mesma versão no Render (`PYTHON_VERSION`) e no ambiente local.
- [ ] **`schema.sql` proposto pelo back-end:** já existe em [`app/database/schema.sql`](app/database/schema.sql) com todas as tabelas que a API usa. Revisar, ajustar e usar como base do [N2-INF-01] (em vez de `src/database/`, que é do código Node). Rodar no Supabase com `python -m app.database.migrate`.
- [ ] **[N2-INF-01] `schema.sql` precisa ter:** `codigo` único na tabela de versões; `gabarito_liberado` (boolean, padrão `false`) na avaliação; `ordem_original` na questão da versão; cópia do enunciado e das alternativas na versão (ver RN14 abaixo).
- [ ] **[N1-INF-02] Script do .zip:** excluir também `.venv/`, `.pytest_cache/` e `.env`.

### 📐 Com a Eloisa (Requisitos, MER e Testes)

- [ ] **[N2-MER-01] / [N2-MER-02] MER e dicionário de dados:** incluir `codigo` da versão, `gabarito_liberado` da avaliação e `ordem_original` da questão na versão.
- [ ] **RN14 (resultados não mudam se a questão for editada):** a versão deve guardar uma **cópia** do enunciado, das alternativas e do gabarito no momento da geração, em vez de só apontar para a questão do banco. Refletir isso no MER.
- [ ] **[N1-REQ-02] Roteiro de testes:** incluir o caso "aluno escaneia o QR Code antes da liberação → vê a mensagem de gabarito não liberado" e "depois da liberação → vê só as letras corretas".
- [ ] **Card [N1-BE-03] cita a regra RN25**, que não existe no documento de requisitos (as regras vão até RN15). Corrigir no backlog.

### 📄 Com o Alyson (Documentação e Arquitetura)

- [ ] **ADR do banco de dados:** a equipe decidiu usar **Supabase (PostgreSQL)**. Como o requisito **RNF08** do documento cita MySQL, registrar em ADR [N2-DOC-01] o motivo da escolha (banco gerenciado em nuvem gratuito, Storage para as fotos das folhas, cliente `supabase-py`).
- [ ] **ADRs das decisões do back-end** listadas acima: gabarito bloqueado até liberar, QR Code com código aleatório e sessão por cookie.
- [ ] **[N1-DOC-02] README v1:** manter as seções "Back-end (API Python)" e "Pontos a Combinar" ao reescrever o README.
- [ ] **Contagem de cards:** o README e o backlog falam em 32 atividades, mas o quadro Kanban tem 36. Ajustar.

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
│   ├── main.py                     # Cria a aplicação e registra os routers
│   ├── core/                       # Configuração e autenticação
│   ├── controllers/                # Rotas HTTP: recebem a requisição e chamam os services
│   ├── services/                   # Regras de negócio (versões, gabaritos, QR Code, correção)
│   ├── repositories/               # Acesso aos dados (consultas ao banco)
│   ├── models/                     # Entidades do domínio
│   └── schemas/                    # Formatos JSON de entrada e saída da API
├── tests/                          # Testes do backend (pytest)
├── requirements.txt                # Dependências de produção
├── requirements-dev.txt            # Dependências de desenvolvimento e testes
├── .env.example                    # Modelo das variáveis de ambiente
└── README.md                       # Documentação principal
```