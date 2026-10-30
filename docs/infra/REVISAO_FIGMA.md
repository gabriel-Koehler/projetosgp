# Conferência parcial do Figma — 05/10/2026

Referência: [Wireframe das telas principais](https://www.figma.com/make/AqsGicfsVgrY5rHqVZ3fFU/Wireframe-das-telas-principais?p=f).

O link respondeu HTTP 200. A miniatura pública do login foi obtida e inspecionada. As demais telas não foram acessadas; a integração Figma foi encontrada, mas não está conectada. Não há aprovação visual completa.

![Miniatura pública do login](figma-thumbnail.webp)

O login é coerente com views/login.ejs: painel verde escuro à esquerda, título “Avaliações do início ao fim, sem esforço.”, funcionalidades e cartão claro à direita com Google, e-mail, senha e botão verde. A imagem não permite validar medidas, tipografia, responsividade ou interações.

| Fluxo documental | Evidência local | Situação |
| --- | --- | --- |
| Login / painel | views/login.ejs, dashboard.ejs, auth.js | Login coerente; Google e recuperação simulados |
| Semestres / turmas / alunos | public/app.js, student-csv.js, /api | Funcional no escopo mock N1 |
| Questões / importação | question-csv.js, CRUD /api | Funcional no escopo N1 |
| Avaliações / versões | app/main.py, public/app.js | Snapshots e configuração em memória |
| Impressão / folha / QR | print.ejs, print.js | Implementado; impressão física pendente |
| Correção / resultados | post-exam.js, /api | Simulação; OMR/Excel reais dependem da N2 |
| Aluno sem conta | student.ejs, gabarito público por token | Publicação explícita e revogável |

A matriz usa o código e docs/requisitos/fluxos-de-usuario.md; não é inspeção de todas as telas Figma. Para aceite completo, acessar o arquivo pela integração ou obter exportação das telas, conferir navegação/retorno, estados vazios/erros, viewport móvel, A4, aluno sem login e liberação/revogação do gabarito.
