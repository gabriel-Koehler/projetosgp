# Diagrama de classes UML v2 — preparação local

Data: 05/10/2026. Campos extraídos dos modelos Python do [PR #45](https://github.com/gabriel-Koehler/projetosgp/pull/45), commit fdb310dac8de60ad10712b79f6fc415aeabe22f2. Essa referência N2 ainda não foi integrada; a main local usa mocks N1.

Fontes: app/models/cadastros.py, avaliacao.py e resultado.py. Métodos hipotéticos do diagrama anterior foram removidos.

```mermaid
classDiagram
    class Professor {
        +int id
        +str username
        +str nome
        +str senha_hash
    }
    class Semestre {
        +int id
        +str nome
        +date_ou_None data_inicio
        +date_ou_None data_fim
        +bool ativo
    }
    class Turma {
        +int id
        +int semestre_id
        +str semestre_nome
        +str nome
        +str_ou_None disciplina
    }
    class Aluno {
        +int id
        +int turma_id
        +str nome
        +str matricula
        +str_ou_None email
    }
    class QuestaoBanco {
        +int id
        +str enunciado
        +list~str~ alternativas
        +str correta
        +str_ou_None disciplina
        +str_ou_None categoria
        +str_ou_None dificuldade
        +bool arquivada
        +datetime_ou_None criado_em
        +datetime_ou_None atualizado_em
    }
    class VersaoAvaliacao {
        +int id
        +str codigo
        +Versao versao
    }
    class ResumoAvaliacao {
        +int id
        +str nome
        +int_ou_None turma_id
        +str_ou_None turma_nome
        +str_ou_None semestre_nome
        +float nota_maxima
        +bool gabarito_liberado
        +datetime criada_em
        +int quantidade_versoes
        +int quantidade_questoes
    }
    class Avaliacao {
        +int id
        +str nome
        +int_ou_None turma_id
        +str_ou_None turma_nome
        +str_ou_None semestre_nome
        +float nota_maxima
        +dict configuracao
        +bool gabarito_liberado
        +datetime criada_em
        +list~VersaoAvaliacao~ versoes
    }
    class VersaoPorCodigo {
        +int avaliacao_id
        +int professor_id
        +str avaliacao_nome
        +bool gabarito_liberado
        +float nota_maxima
        +int versao_id
        +str versao_nome
        +dict~int_str~ gabarito
        +dict~int_int~ alternativas_por_questao
    }
    class Resultado {
        +int id
        +int avaliacao_id
        +str avaliacao_nome
        +int versao_id
        +str versao_nome
        +int_ou_None aluno_id
        +str_ou_None aluno_nome
        +str_ou_None matricula
        +str_ou_None turma_nome
        +str_ou_None semestre_nome
        +dict~int_str_ou_None~ respostas
        +dict~int_str~ gabarito
        +int acertos
        +int erros
        +int em_branco
        +int anuladas
        +float nota
        +float nota_maxima
        +str origem
        +str_ou_None imagem_path
        +datetime corrigido_em
    }
    class QuestaoDaVersao {
        +int versao_id
        +int numero
        +int_ou_None questao_id
        +str enunciado
        +list~str~ ordem_original
    }
    Professor "1" --> "0..*" Semestre : propriedade SQL
    Semestre "1" --> "0..*" Turma
    Turma "1" --> "0..*" Aluno
    Professor "1" --> "0..*" QuestaoBanco
    Avaliacao "1" *-- "0..*" VersaoAvaliacao
    VersaoAvaliacao --> Versao
    Versao "1" *-- "0..*" QuestaoVersao
    Resultado --> Avaliacao
    Resultado --> VersaoAvaliacao
    Resultado --> Aluno : opcional
```

## Correspondência e limites

- Professor, Semestre, Turma e Aluno correspondem às tabelas homônimas em minúsculas.
- QuestaoBanco corresponde a questao/alternativa; Avaliacao a avaliacao/avaliacao_questao.
- VersaoAvaliacao/Versao correspondem a versao_avaliacao; QuestaoVersao a questao_versao/gabarito_versao.
- Resultado corresponde a resultado_correcao. ResumoAvaliacao, VersaoPorCodigo e QuestaoDaVersao são projeções de consultas.
- FolhaResposta não é uma classe persistida autônoma nesse contrato: respostas, gabarito e imagem ficam no resultado.
- Core local N1: app/core/version_builder.py possui Questao, ConfiguracaoVersoes, QuestaoVersao, Versao e Nomenclatura. A N2 evolui esse core em app/services/version_builder.py.
- Reconferir após integração dos PRs N2; diagrama não certifica implantação ou homologação N2.
