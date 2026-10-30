# DER físico — N2-INF-01

Preparação local de Diego em 05/10/2026. Contrato do [PR #45](https://github.com/gabriel-Koehler/projetosgp/pull/45), commit fdb310dac8de60ad10712b79f6fc415aeabe22f2, ainda não integrado à main. A aplicação N1 permanece em memória.

```mermaid
erDiagram
    professor {
        BIGSERIAL id PK
        TEXT username
        TEXT nome
        TEXT senha_hash
        TIMESTAMPTZ criado_em
    }
    semestre {
        BIGSERIAL id PK
        BIGINT professor_id FK
        TEXT nome
        DATE data_inicio
        DATE data_fim
        BOOLEAN ativo
        TIMESTAMPTZ criado_em
    }
    professor ||--o{ semestre : referencia
    turma {
        BIGSERIAL id PK
        BIGINT semestre_id FK
        TEXT nome
        TEXT disciplina
        TIMESTAMPTZ criado_em
    }
    semestre ||--o{ turma : referencia
    aluno {
        BIGSERIAL id PK
        BIGINT turma_id FK
        TEXT nome
        TEXT matricula
        TEXT email
        TIMESTAMPTZ criado_em
    }
    turma ||--o{ aluno : referencia
    questao {
        BIGSERIAL id PK
        BIGINT professor_id FK
        TEXT enunciado
        CHAR1 correta
        TEXT disciplina
        TEXT categoria
        TEXT dificuldade
        BOOLEAN arquivada
        TIMESTAMPTZ criado_em
        TIMESTAMPTZ atualizado_em
    }
    professor ||--o{ questao : referencia
    alternativa {
        BIGSERIAL id PK
        BIGINT questao_id FK
        CHAR1 letra
        TEXT texto
    }
    questao ||--o{ alternativa : referencia
    avaliacao {
        BIGSERIAL id PK
        BIGINT professor_id FK
        BIGINT turma_id FK
        TEXT nome
        JSONB configuracao
        NUMERIC62 nota_maxima
        BOOLEAN gabarito_liberado
        TIMESTAMPTZ criada_em
    }
    professor ||--o{ avaliacao : referencia
    turma |o--o{ avaliacao : referencia
    avaliacao_questao {
        BIGINT avaliacao_id FK
        BIGINT questao_id FK
        INT ordem
        CHAR1 correta
    }
    avaliacao ||--o{ avaliacao_questao : referencia
    questao ||--o{ avaliacao_questao : referencia
    versao_avaliacao {
        BIGSERIAL id PK
        BIGINT avaliacao_id FK
        TEXT nome
        TEXT codigo
        INT ordem
    }
    avaliacao ||--o{ versao_avaliacao : referencia
    questao_versao {
        BIGSERIAL id PK
        BIGINT versao_id FK
        INT numero
        BIGINT questao_id FK
        TEXT enunciado
        JSONB alternativas
        JSONB ordem_original
    }
    versao_avaliacao ||--o{ questao_versao : referencia
    questao |o--o{ questao_versao : referencia
    gabarito_versao {
        BIGINT versao_id FK
        INT numero
        CHAR1 correta
    }
    versao_avaliacao ||--o{ gabarito_versao : referencia
    resultado_correcao {
        BIGSERIAL id PK
        BIGINT avaliacao_id FK
        BIGINT versao_id FK
        BIGINT aluno_id FK
        JSONB respostas
        JSONB gabarito
        INT acertos
        INT erros
        INT em_branco
        INT anuladas
        NUMERIC62 nota
        NUMERIC62 nota_maxima
        TEXT origem
        TEXT imagem_path
        TIMESTAMPTZ corrigido_em
    }
    avaliacao ||--o{ resultado_correcao : referencia
    versao_avaliacao ||--o{ resultado_correcao : referencia
    aluno |o--o{ resultado_correcao : referencia
```

## Integridade e operação

- Chaves compostas: avaliacao_questao(avaliacao_id, questao_id), gabarito_versao(versao_id, numero).
- questao_versao preserva snapshots de enunciado, alternativas e ordem original. Gabaritos são próprios de cada versão.
- Resultado por aluno/avaliação é único quando há aluno identificado.
- RLS habilitada sem policies públicas: usar acesso PostgreSQL pelo servidor com papel adequado. Manter autorização por professor nos repositories/services.
- O contrato original valida relações professor/turma e aluno/versão nos services; revisar constraints compostas após integração.
- IF NOT EXISTS não atualiza tabelas existentes. Aplicar em banco vazio; não usar como migração do schema inglês/UUID anterior.
- Execução DDL/seed e homologação pendentes: PostgreSQL e Docker ausentes no ambiente.
