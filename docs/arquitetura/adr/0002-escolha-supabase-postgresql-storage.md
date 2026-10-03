# ADR-0002: Adoção do Supabase (PostgreSQL Cloud + Supabase Storage)

* **Status:** Aprovado
* **Data:** Outubro de 2024 (Fase N2)
* **Autor / Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Revisor:** Luan Eliseu / Gabriel Koehler da Silva
* **Contexto:** [N2-DOC-01] Passo 02 e Critério C3 (20% da N2)

---

## 1. Contexto e Problema

O Sistema SGP exige persistência de dados de alta integridade para estruturar todo o domínio acadêmico:
* Gestão de semestres letivos, turmas, alunos e professores.
* Banco de questões, enunciados, tipos e alternativas.
* Avaliações geradas, controle de múltiplas versões (ex: A, B, C) e gabaritos associados.
* Registro individual de correções, alternativas lidas, notas calculadas e status da correção.

Além disso, é fundamental persistir os arquivos binários das folhas de respostas escaneadas/fotografadas (para fins de auditoria, histórico e conferência manual pelo professor). Salvar arquivos binários (BLOBs) diretamente dentro do banco de dados relacional causa inchaço desnecessário da base (*database bloat*), enquanto salvá-los no disco local do servidor inviabiliza o deploy em plataformas modernas de nuvem (Render, Vercel, Fly.io), cujos sistemas de arquivos são efêmeros.

---

## 2. Decisão Arquitetural

Decidiu-se adotar a plataforma **Supabase** como a solução oficial de banco de dados e armazenamento de arquivos em nuvem:
1. **Supabase PostgreSQL:** Instância de PostgreSQL 15+ totalmente gerenciada na nuvem, com suporte nativo a constraints de integridade referencial (`FOREIGN KEY`, `ON DELETE CASCADE/RESTRICT`, `CHECK`), tipos relacionais rígidos e suporte a colunas `JSONB` quando oportuno.
2. **Supabase Storage:** Buckets de armazenamento de objetos compatíveis com S3 para armazenar:
   * A imagem original enviada pelo professor (`/answer-sheets/originals/`).
   * A imagem anotada gerada pelo OpenCV com as marcações de acerto/erro (`/answer-sheets/annotated/`).
3. **supabase-py:** Biblioteca oficial em Python para integração assíncrona/síncrona com os repositórios da aplicação.
4. **Supavisor:** Utilização do connection pooler nativo para assegurar estabilidade de conexões sob requisições concorrentes.

---

## 3. Alternativas Avaliadas

### Alternativa A: SQLite Local
* **Pontos Negativos:** Inviável para ambientes de nuvem efêmeros (onde o disco é reiniciado a cada novo deploy). Não possui concorrência de escrita nem suporte a múltiplos nós de backend.

### Alternativa B: Bancos de Dados NoSQL / Não-Relacionais (ex: MongoDB, Firebase Firestore)
* **Pontos Negativos:** O domínio do SGP é inerentemente relacional. A ausência de constraints de integridade referencial automáticas no banco exigiria validações complexas e propensas a falhas na camada de aplicação, arriscando gerar orfandade de dados (ex: uma correção apontando para uma versão inexistente).

### Alternativa C: PostgreSQL Auto-Hospedado em Servidor VPS (ex: EC2, DigitalOcean)
* **Pontos Negativos:** Exigiria manutenção contínua de infraestrutura, rotinas manuais de backup, configuração manual de certificados SSL, provisionamento de S3 separado e regras de firewall, aumentando desnecessariamente a complexidade do projeto acadêmico.

---

## 4. Consequências da Decisão

### Consequências Positivas:
* **Conformidade ACID e Integridade:** Garantia absoluta de que relacionamentos entre provas, versões, gabaritos e notas são consistentes.
* **Storage Integrado:** Uma única plataforma gerencia tanto os dados relacionais quanto os arquivos estáticos de imagem.
* **Agilidade no Desenvolvimento:** A interface administrativa do Supabase (*Studio*) facilita a inspeção visual dos dados e execução de scripts de migração (`schema.sql` e `seed.sql`).
* **Custo Zero (Tier Gratuito Amplo):** O plano gratuito do Supabase atende com folga toda a demanda da disciplina sem custos de infraestrutura.

### Consequências Negativas e Mitigações:
* **Conexão Externa:** Requer conexão de rede ativa para acesso ao banco durante o desenvolvimento.  
  * *Mitigação:* Os scripts DDL (`src/database/schema.sql` e `seed.sql`) são totalmente compatíveis com instâncias locais do PostgreSQL via Docker, permitindo desenvolvimento offline se necessário.
