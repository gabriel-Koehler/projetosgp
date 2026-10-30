# Integração dos PRs N1 restantes

A main mantém a API compatível com o frontend em /api. Os PRs BE-01/03/04 possuem contratos distintos (username, questões completas e identificadores numéricos); a aplicação modular é exposta em /n1 na porta 8000, com sua documentação em /n1/docs. Essa separação preserva ambos os contratos e as sessões sem substituir rotas do MVP.

A fábrica app.backend:create_app também permite executar o backend modular isoladamente: uvicorn app.backend:create_app --factory --port 8001. Nesse modo, as rotas originais ficam na raiz. As configurações constam em .env.example.

Validação conjunta: pytest e testes Node. A unificação futura dos contratos e da persistência faz parte das integrações N2.
