# Validação local — 05/10/2026

Base: 972a760; branch infra/diego-entregas-locais.

| Verificação | Resultado |
| --- | --- |
| Testes Node | 8 aprovados |
| Suite Python | Primeira execução: 118 aprovados em 4,90 s. Repetição final: 117 aprovados e 1 falha na leitura do QR; caso isolado passou em 1,55 s. Dependências temporárias e cache desativado |
| Cookie HTTPS | true/false validados na suite Python |
| Empacotador | Exclusões, geração repetida e extração aprovadas |
| Frontend / saúde | Login renderizado; /health 200 com API e 503 sem API |
| Sintaxe JavaScript | server.js, start-hosted.js e start-mvp.js verificados |
| Docker / PostgreSQL | Não executados: ferramentas ausentes |
| Supabase / deploy | Não executados: escopo exclusivamente local |
| Figma | Miniatura de login coerente; demais telas pendentes |

Dependências instaladas e validadas em pasta temporária local. A instalação da .venv no workspace não foi concluída; reinstalar antes de executar nela. Não foram alteradas as versões do lockfile. npm informou quatro vulnerabilidades no conjunto de dependências: três moderadas e uma alta; revisão da equipe pendente.

A checagem final identificou corrupção após gravação direta no workspace. Os artefatos foram reconstruídos em pasta temporária e copiados para o projeto; conferir integridade dos ZIPs e arquivos antes de entrega. O pacote N2 representa preparação e não homologação final. Nenhuma issue foi encerrada.

Os dois ZIPs finais foram conferidos com 92 arquivos cada, CRC íntegro, texto UTF-8 válido e extração concluída. Segredos e artefatos locais excluídos. A falha de QR é intermitente nas execuções observadas; estabilidade da geração/leitura deve ser revisada antes da homologação.
