-- Esquema do banco (PostgreSQL / Supabase).
-- Proposta do back-end para o card [N2-INF-01]: o Diego revisa e ajusta.
-- Idempotente: pode rodar várias vezes (python -m app.database.migrate).
--
-- Relação principal (RNF07):
--   Professor -> Semestre -> Turma -> Aluno
--   Professor -> Questao -> Alternativa
--   Avaliacao -> VersaoAvaliacao -> QuestaoVersao / GabaritoVersao -> ResultadoCorrecao

CREATE TABLE IF NOT EXISTS professor (
    id          BIGSERIAL PRIMARY KEY,
    username    TEXT NOT NULL UNIQUE,
    nome        TEXT NOT NULL,
    senha_hash  TEXT NOT NULL,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RF02
CREATE TABLE IF NOT EXISTS semestre (
    id            BIGSERIAL PRIMARY KEY,
    professor_id  BIGINT NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    nome          TEXT NOT NULL,
    data_inicio   DATE,
    data_fim      DATE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (professor_id, nome),
    CHECK (data_inicio IS NULL OR data_fim IS NULL OR data_fim >= data_inicio)
);

-- RF03
CREATE TABLE IF NOT EXISTS turma (
    id           BIGSERIAL PRIMARY KEY,
    semestre_id  BIGINT NOT NULL REFERENCES semestre(id) ON DELETE RESTRICT,
    nome         TEXT NOT NULL,
    disciplina   TEXT,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (semestre_id, nome)
);

-- RF04
CREATE TABLE IF NOT EXISTS aluno (
    id         BIGSERIAL PRIMARY KEY,
    turma_id   BIGINT NOT NULL REFERENCES turma(id) ON DELETE RESTRICT,
    nome       TEXT NOT NULL,
    matricula  TEXT NOT NULL,
    email      TEXT,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (turma_id, matricula)
);

-- RF06 a RF09. "arquivada" = excluída do banco de questões, mas mantida
-- porque já foi usada em alguma avaliação (RF08).
CREATE TABLE IF NOT EXISTS questao (
    id             BIGSERIAL PRIMARY KEY,
    professor_id   BIGINT NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    enunciado      TEXT NOT NULL,
    correta        CHAR(1) NOT NULL CHECK (correta ~ '^[A-Z]$'),
    disciplina     TEXT,
    categoria      TEXT,
    dificuldade    TEXT CHECK (dificuldade IN ('facil', 'media', 'dificil')),
    arquivada      BOOLEAN NOT NULL DEFAULT FALSE,
    criado_em      TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alternativa (
    id          BIGSERIAL PRIMARY KEY,
    questao_id  BIGINT NOT NULL REFERENCES questao(id) ON DELETE CASCADE,
    letra       CHAR(1) NOT NULL CHECK (letra ~ '^[A-Z]$'),
    texto       TEXT NOT NULL,
    UNIQUE (questao_id, letra)
);

-- RF14. configuracao guarda as opções de geração das versões (RF17 a RF22).
CREATE TABLE IF NOT EXISTS avaliacao (
    id                 BIGSERIAL PRIMARY KEY,
    professor_id       BIGINT NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    turma_id           BIGINT REFERENCES turma(id) ON DELETE RESTRICT,
    nome               TEXT NOT NULL,
    configuracao       JSONB NOT NULL,
    nota_maxima        NUMERIC(6, 2) NOT NULL DEFAULT 10 CHECK (nota_maxima > 0),
    -- Consulta do gabarito pelo QR Code bloqueada até o professor liberar.
    gabarito_liberado  BOOLEAN NOT NULL DEFAULT FALSE,
    criada_em          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RF15 e RF16: questões selecionadas e o gabarito definido para esta avaliação.
CREATE TABLE IF NOT EXISTS avaliacao_questao (
    avaliacao_id  BIGINT NOT NULL REFERENCES avaliacao(id) ON DELETE CASCADE,
    questao_id    BIGINT NOT NULL REFERENCES questao(id) ON DELETE RESTRICT,
    ordem         INT NOT NULL,
    correta       CHAR(1) NOT NULL CHECK (correta ~ '^[A-Z]$'),
    PRIMARY KEY (avaliacao_id, questao_id)
);

-- RF23. codigo vai no QR Code (RF28) e identifica a versão na correção (RF32).
CREATE TABLE IF NOT EXISTS versao_avaliacao (
    id            BIGSERIAL PRIMARY KEY,
    avaliacao_id  BIGINT NOT NULL REFERENCES avaliacao(id) ON DELETE CASCADE,
    nome          TEXT NOT NULL,
    codigo        TEXT NOT NULL UNIQUE,
    ordem         INT NOT NULL,
    UNIQUE (avaliacao_id, nome)
);

-- Cópia da questão no momento da geração (RN14): editar a questão no banco
-- depois não altera provas nem resultados já registrados.
CREATE TABLE IF NOT EXISTS questao_versao (
    id              BIGSERIAL PRIMARY KEY,
    versao_id       BIGINT NOT NULL REFERENCES versao_avaliacao(id) ON DELETE CASCADE,
    numero          INT NOT NULL,
    questao_id      BIGINT REFERENCES questao(id) ON DELETE SET NULL,
    enunciado       TEXT NOT NULL,
    alternativas    JSONB NOT NULL,   -- textos na ordem desta versão
    ordem_original  JSONB NOT NULL,   -- letra original de cada alternativa exibida
    UNIQUE (versao_id, numero)
);

-- RF24: gabarito próprio de cada versão.
CREATE TABLE IF NOT EXISTS gabarito_versao (
    versao_id  BIGINT NOT NULL REFERENCES versao_avaliacao(id) ON DELETE CASCADE,
    numero     INT NOT NULL,
    correta    CHAR(1) NOT NULL CHECK (correta ~ '^[A-Z]$'),
    PRIMARY KEY (versao_id, numero)
);

-- RF39. respostas e gabarito são cópias ({"1": "A", "2": null, ...}).
CREATE TABLE IF NOT EXISTS resultado_correcao (
    id            BIGSERIAL PRIMARY KEY,
    avaliacao_id  BIGINT NOT NULL REFERENCES avaliacao(id) ON DELETE CASCADE,
    versao_id     BIGINT NOT NULL REFERENCES versao_avaliacao(id) ON DELETE CASCADE,
    aluno_id      BIGINT REFERENCES aluno(id) ON DELETE SET NULL,
    respostas     JSONB NOT NULL,
    gabarito      JSONB NOT NULL,
    acertos       INT NOT NULL,
    erros         INT NOT NULL,
    em_branco     INT NOT NULL,
    anuladas      INT NOT NULL,   -- mais de uma alternativa marcada
    nota          NUMERIC(6, 2) NOT NULL,
    nota_maxima   NUMERIC(6, 2) NOT NULL,
    origem        TEXT NOT NULL CHECK (origem IN ('omr', 'manual')),
    imagem_path   TEXT,           -- foto da folha no Supabase Storage
    corrigido_em  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Um resultado por aluno em cada avaliação (nova correção substitui a anterior).
CREATE UNIQUE INDEX IF NOT EXISTS resultado_aluno_unico
    ON resultado_correcao (avaliacao_id, aluno_id) WHERE aluno_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_turma_semestre ON turma (semestre_id);
CREATE INDEX IF NOT EXISTS idx_aluno_turma ON aluno (turma_id);
CREATE INDEX IF NOT EXISTS idx_questao_professor ON questao (professor_id) WHERE NOT arquivada;
CREATE INDEX IF NOT EXISTS idx_avaliacao_professor ON avaliacao (professor_id);
CREATE INDEX IF NOT EXISTS idx_versao_avaliacao ON versao_avaliacao (avaliacao_id);
CREATE INDEX IF NOT EXISTS idx_resultado_avaliacao ON resultado_correcao (avaliacao_id);
