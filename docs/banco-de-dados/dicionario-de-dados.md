# Dicionário de Dados — PostgreSQL/Supabase

**Issue:** N2-MER-02 · **Etapa:** N2 – Passo 02 (Modelar Banco e ADRs)
**Critério avaliado:** C3 — Documentação (README v2): modelo de dados
**Responsável:** Eloisa Fazzio da Silva Rocha
**Base:** [`docs/banco-de-dados/mer-conceitual.md`](./mer-conceitual.md)

> ⚠️ O Documento de Requisitos original (RNF08) especifica MySQL. Este dicionário assume **PostgreSQL via Supabase**, conforme pedido nesta issue — confirmar com a equipe se houve mudança de stack e, se sim, registrar a decisão em um ADR (`docs/banco-de-dados/adr-supabase.md`).

> Convenções: chaves primárias `id` do tipo `uuid` (`default gen_random_uuid()`, padrão Supabase); nomes de tabela e coluna em `snake_case`; toda tabela possui `created_at timestamptz default now()`, omitido nas tabelas abaixo por brevidade e listado apenas onde há campos de auditoria adicionais.

---

## Índice de tabelas

| # | Tabela | Entidade conceitual correspondente |
|---|---|---|
| 1 | `professores` | Professor |
| 2 | `semestres` | Semestre |
| 3 | `turmas` | Turma |
| 4 | `alunos` | Aluno |
| 5 | `questoes` | Questão |
| 6 | `alternativas` | Alternativa |
| 7 | `avaliacoes` | Avaliação |
| 8 | `versoes` | Versão |
| 9 | `versao_questoes` | Versão_Questão (associativa) |
| 10 | `resultados` | Resultado |
| 11 | `respostas` | Resposta |

---

## 1. `professores`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `nome` | `text` | NOT NULL | Nome completo do professor |
| `email` | `text` | NOT NULL, UNIQUE | Usado no login (RF01) |
| `senha_hash` | `text` | NOT NULL | Senha armazenada com hash (nunca em texto puro) |
| `created_at` | `timestamptz` | NOT NULL, default `now()` | Auditoria |

**Regras de integridade:** RN01 (único perfil autenticado do sistema); `email` único garante login sem ambiguidade.

---

## 2. `semestres`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `professor_id` | `uuid` | NOT NULL, FK → `professores.id` ON DELETE RESTRICT | Professor responsável (RF02) |
| `nome` | `text` | NOT NULL | Ex.: "2026/2" |
| `data_inicio` | `date` | NOT NULL | |
| `data_fim` | `date` | NOT NULL, CHECK (`data_fim >= data_inicio`) | |
| `ativo` | `boolean` | NOT NULL, default `true` | Permite ativar/desativar (RF02) |

---

## 3. `turmas`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `semestre_id` | `uuid` | NOT NULL, FK → `semestres.id` ON DELETE CASCADE | (RF03) |
| `nome` | `text` | NOT NULL | |

**Regras de integridade:** UNIQUE (`semestre_id`, `nome`) — não permitir turmas com nome duplicado no mesmo semestre.

---

## 4. `alunos`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `turma_id` | `uuid` | NOT NULL, FK → `turmas.id` ON DELETE CASCADE | (RF04) |
| `nome` | `text` | NOT NULL | |
| `matricula` | `text` | NOT NULL | |

**Regras de integridade:** UNIQUE (`turma_id`, `matricula`) — matrícula não se repete na mesma turma. O aluno **não** possui login/senha (RN02) — tabela intencionalmente sem credenciais.

---

## 5. `questoes`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `professor_id` | `uuid` | NOT NULL, FK → `professores.id` ON DELETE RESTRICT | Quem cadastrou/importou (RF06, RF10) |
| `enunciado` | `text` | NOT NULL | |
| `disciplina` | `text` | NULL | Campo opcional (RF06) |
| `categoria` | `text` | NULL | Campo opcional |
| `dificuldade` | `text` | NULL, CHECK (`dificuldade IN ('facil','media','dificil')`) | Campo opcional |
| `origem` | `text` | NOT NULL, CHECK (`origem IN ('manual','importada')`), default `'manual'` | Rastreia RF06 vs RF10 |
| `excluida_em` | `timestamptz` | NULL | Soft delete — ver regra abaixo |

**Regras de integridade:**
- RF08: exclusão não pode comprometer avaliações/resultados históricos → usar **soft delete** (`excluida_em`), nunca `DELETE` físico se a questão já foi usada em alguma `versao_questoes`.
- RN14: editar uma questão do banco não deve alterar resultados já registrados → `versao_questoes` e `respostas` **não referenciam `questoes` para exibição histórica de enunciado/alternativas**; guardam uma cópia (`enunciado_snapshot`, ver tabela 9) para preservar o que foi efetivamente aplicado.

---

## 6. `alternativas`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `questao_id` | `uuid` | NOT NULL, FK → `questoes.id` ON DELETE CASCADE | |
| `letra` | `char(1)` | NOT NULL, CHECK (`letra IN ('A','B','C','D')`) | |
| `texto` | `text` | NOT NULL | |
| `correta` | `boolean` | NOT NULL, default `false` | Gabarito-base da questão |

**Regras de integridade:**
- UNIQUE (`questao_id`, `letra`) — não repetir letra na mesma questão.
- Exatamente uma alternativa `correta = true` por questão — validado via trigger/constraint de aplicação (Postgres não garante nativamente "exatamente uma" entre linhas sem trigger).
- RN07: a alternativa marcada como `correta` nunca é alterada pelo embaralhamento — o embaralhamento só afeta a ordem de exibição, registrada em `versao_questoes`.

---

## 7. `avaliacoes`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `professor_id` | `uuid` | NOT NULL, FK → `professores.id` ON DELETE RESTRICT | (RF14) |
| `turma_id` | `uuid` | NOT NULL, FK → `turmas.id` ON DELETE RESTRICT | (RF14) |
| `nome` | `text` | NOT NULL | |
| `data_aplicacao` | `date` | NULL | |
| `destinatario` | `text` | NULL | |
| `embaralhar_questoes` | `boolean` | NOT NULL, default `false` | RN09 |
| `embaralhar_alternativas` | `boolean` | NOT NULL, default `false` | RN10 |
| `mesmas_questoes_todas_versoes` | `boolean` | NOT NULL, default `true` | RN11 |

---

## 8. `versoes`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `avaliacao_id` | `uuid` | NOT NULL, FK → `avaliacoes.id` ON DELETE CASCADE | Uma avaliação possui várias versões (seção 8 do doc. de requisitos) |
| `identificacao` | `text` | NOT NULL | Ex.: "A", "B", "Azul" (RF18) |
| `qr_code_url` | `text` | NULL | Preenchido após geração (RF28) |

**Regras de integridade:** UNIQUE (`avaliacao_id`, `identificacao`) — não repetir identificação de versão na mesma avaliação (RN08).

---

## 9. `versao_questoes` (associativa — gabarito por versão)

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `versao_id` | `uuid` | NOT NULL, FK → `versoes.id` ON DELETE CASCADE | |
| `questao_id` | `uuid` | NOT NULL, FK → `questoes.id` ON DELETE RESTRICT | |
| `ordem_apresentacao` | `integer` | NOT NULL | Posição da questão na versão (embaralhamento de questões — RN09) |
| `ordem_alternativas` | `jsonb` | NOT NULL | Ex.: `["C","A","D","B"]` — ordem de exibição das letras nesta versão |
| `alternativa_correta_id` | `uuid` | NOT NULL, FK → `alternativas.id` | Qual alternativa é a correta **nesta versão** (RN06) |
| `enunciado_snapshot` | `text` | NOT NULL | Cópia do enunciado no momento da geração da versão — preserva histórico (RN14) |

**Regras de integridade:**
- UNIQUE (`versao_id`, `questao_id`) — questão não se repete na mesma versão.
- UNIQUE (`versao_id`, `ordem_apresentacao`) — não há duas questões na mesma posição.
- `alternativa_correta_id` deve pertencer a `questao_id` (checagem de aplicação/trigger, já que FK simples não garante o relacionamento cruzado).
- RF25: ao embaralhar, `ordem_alternativas` muda, mas `alternativa_correta_id` sempre aponta para a alternativa cujo `correta = true` em `alternativas` — a posição visual muda, o gabarito real não.

---

## 10. `resultados`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `versao_id` | `uuid` | NOT NULL, FK → `versoes.id` ON DELETE RESTRICT | (RF39) |
| `aluno_id` | `uuid` | NULL, FK → `alunos.id` ON DELETE SET NULL | "Aluno quando associado" (RF39) |
| `acertos` | `integer` | NOT NULL, CHECK (`acertos >= 0`) | |
| `erros` | `integer` | NOT NULL, CHECK (`erros >= 0`) | |
| `nota` | `numeric(5,2)` | NOT NULL | |
| `data_hora` | `timestamptz` | NOT NULL, default `now()` | |
| `leitura_confiavel` | `boolean` | NOT NULL, default `true` | RN15 — resultado só é definitivo se `true` |

**Regras de integridade:** RN15 — leitura inválida/duvidosa não gera resultado definitivo automaticamente; a aplicação só deve persistir uma linha aqui quando `leitura_confiavel = true` (caso contrário, o fluxo de correção pede nova leitura sem gravar).

---

## 11. `respostas`

| Coluna | Tipo | Constraints | Descrição |
|---|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` | Identificador único |
| `resultado_id` | `uuid` | NOT NULL, FK → `resultados.id` ON DELETE CASCADE | |
| `versao_questao_id` | `uuid` | NOT NULL, FK → `versao_questoes.id` ON DELETE RESTRICT | Referencia a questão *dentro da versão* aplicada, não a questão "solta" |
| `alternativa_marcada` | `char(1)` | NULL, CHECK (`alternativa_marcada IN ('A','B','C','D') OR alternativa_marcada IS NULL`) | `NULL` = ausência/ilegível (RF36) |
| `correta` | `boolean` | NOT NULL | Calculado comparando `alternativa_marcada` com o gabarito da versão (RF42) |

**Regras de integridade:**
- UNIQUE (`resultado_id`, `versao_questao_id`) — uma resposta por questão por resultado.
- RF36/RF40: `alternativa_marcada = NULL` representa ausência, múltipla marcação ou marcação ilegível — nesses casos a aplicação **não** deve criar o `resultado` pai como definitivo (ver regra da tabela 10).

---

## Resumo — mapeamento de regras de negócio → constraints

| Regra | Onde é aplicada no banco |
|---|---|
| RN01 — único autenticado | Login restrito a `professores`; `alunos` sem credenciais |
| RN02 — aluno sem conta | `alunos` não possui coluna de senha/login |
| RN06 — gabarito próprio por versão | `versao_questoes.alternativa_correta_id` |
| RN07 — embaralhamento não altera resposta correta | `alternativas.correta` imutável; só `versao_questoes.ordem_alternativas` muda |
| RN08 — quantidade de versões definida pelo professor | Sem limite de linhas em `versoes`; UI controla a criação |
| RN09/RN10 — embaralhar questões/alternativas | Flags em `avaliacoes`; efeito registrado em `versao_questoes` |
| RN11 — mesmas questões ou conjuntos diferentes | `avaliacoes.mesmas_questoes_todas_versoes` |
| RN14 — edição de questão não altera resultados antigos | `versao_questoes.enunciado_snapshot` congela o conteúdo aplicado |
| RN15 — leitura duvidosa não gera resultado definitivo | `resultados.leitura_confiavel`; aplicação só persiste quando `true` |
| RNF07 — integridade Avaliação→Versão→Questões→Alternativas→Gabarito→Respostas→Resultado | Cadeia de FKs: `avaliacoes` → `versoes` → `versao_questoes` → `questoes`/`alternativas`; `resultados` → `respostas` → `versao_questoes` |

---

## Próximos passos (fora do escopo desta issue)

- Criar as migrations SQL no Supabase a partir deste dicionário.
- Configurar Row Level Security (RLS) no Supabase: `professores` só acessa seus próprios dados; tabela pública somente para a leitura de gabarito via QR Code (RF29/RF30), sem expor `resultados`/`respostas`.
- Registrar a escolha de Supabase/PostgreSQL (em vez do MySQL previsto em RNF08) em um ADR.
