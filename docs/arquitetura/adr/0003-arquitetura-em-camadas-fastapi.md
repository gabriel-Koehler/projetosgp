# ADR-0003: Adoção da Arquitetura em Camadas e FastAPI no Backend

* **Status:** Aprovado
* **Data:** Outubro de 2024 (Fase N2)
* **Autor / Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Revisor:** Luan Eliseu / Gabriel Koehler da Silva
* **Contexto:** [N2-DOC-01] Passo 02 e Critério C3 (20% da N2)

---

## 1. Contexto e Problema

Na Fase N1 do projeto, a equipe construiu um protótipo focado na validação de telas navegáveis e experiência de usuário (usando Node.js/Express e estado em memória). 

Para a Fase N2, surgiram requisitos mais complexos e desafiadores:
* Integração nativa com bibliotecas de visão computacional em Python (OpenCV e pyzbar).
* Persistência em banco de dados relacional (Supabase/PostgreSQL).
* Necessidade de isolar as regras de negócio (cálculo de notas, algoritmos de embaralhamento de versões) tanto do framework web quanto do banco de dados.
* Necessidade de documentação clara e contratos de API padronizados para permitir o desenvolvimento paralelo entre a equipe de frontend e backend.

Era imperativo definir um padrão arquitetural sólido e escolher o framework de backend que oferecesse a melhor performance e produtividade.

---

## 2. Decisão Arquitetural

Decidiu-se estruturar o backend seguindo o padrão de **Arquitetura em Camadas (Layered Architecture)**, utilizando **Python 3.11** com o framework **FastAPI**:

1. **Separação Rígida em Camadas:**
   * **Camada de Apresentação (UI):** Interfaces web (HTML5/CSS3/JS) consumindo a API REST.
   * **Camada de Aplicação / Controladores (API):** Rotas FastAPI, injeção de dependência e DTOs Pydantic.
   * **Camada de Domínio:** Entidades puras e serviços de negócio (`ExamService`, `GradingService`, `ShufflingService`).
   * **Camada de Visão Computacional (OMR):** Módulo dedicado encapsulando o processamento do OpenCV/pyzbar.
   * **Camada de Repositórios / Acesso a Dados:** Padrão Repository encapsulando chamadas ao `supabase-py`.
   * **Camada de Infraestrutura:** Supabase PostgreSQL e Supabase Storage.
2. **Framework FastAPI:**
   * Operação sobre servidor ASGI de alta performance (Uvicorn).
   * Validação estrita de contratos de entrada e saída com schemas Pydantic v2.
   * Documentação automática interativa com Swagger UI (`/docs`) e ReDoc (`/redoc`).

---

## 3. Alternativas Avaliadas

### Alternativa A: Backend Híbrido (Manter Node.js/Express e disparar scripts Python via Subprocessos)
* **Pontos Negativos:** Iniciar o interpretador Python a cada folha corrigida gera um overhead de 1 a 3 segundos apenas de inicialização do processo. Além disso, a troca de dados por arquivos temporários ou pipes dificulta a depuração e o tratamento de exceções.

### Alternativa B: Framework Django (Python)
* **Pontos Negativos:** Estrutura monolítica excessivamente pesada ("batteries included"), com ORM próprio acoplado que entraria em conflito com o modelo de integração leve e moderno do Supabase, além de menor performance assíncrona.

### Alternativa C: Framework Flask (Python)
* **Pontos Negativos:** Não oferece validação nativa por tipagem de dados, suporte a requisições assíncronas é limitado e requer plugins externos para documentação Swagger.

---

## 4. Consequências da Decisão

### Consequências Positivas:
* **Interoperabilidade Total na Memória RAM:** A imagem enviada pelo frontend via upload chega à API e é repassada diretamente como um array NumPy (`numpy.ndarray`) para o OpenCV, sem nenhum acesso intermediário a disco, resultando em velocidade máxima de correção (< 1.5s por prova).
* **Baixo Acoplamento e Alta Coesão:** Alterações nas regras de negócio (ex: mudar a fórmula de cálculo da nota) não impactam os controladores nem o banco de dados.
* **Documentação Viva e Interativa:** A rota `/docs` permite que a equipe de frontend teste endpoints imediatamente, com documentação gerada automaticamente a partir do código.
* **Conformidade Pedagógica e Arquitetural:** Atende com excelência aos preceitos da disciplina de Projeto e Arquitetura de Software.

### Consequências Negativas e Mitigações:
* **Concorrência em Tarefas de CPU-Bound:** O processamento de imagem do OpenCV consome processador e pode bloquear o event loop assíncrono se não for bem gerenciado.  
  * *Mitigação:* As rotas de processamento de imagem são declaradas como funções síncronas convencionais (`def`) ou despachadas via `run_in_threadpool`, fazendo com que o FastAPI as execute em um pool de threads separado, mantendo a API 100% responsiva para outras requisições.
