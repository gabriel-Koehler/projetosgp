# ADR-0001: Adoção do Python e OpenCV para Visão Computacional e OMR

* **Status:** Aprovado
* **Data:** Outubro de 2024 (Fase N2)
* **Autor / Responsável:** ALYSON DE LIMA DE OLIVEIRA
* **Revisor:** Luan Eliseu / Gabriel Koehler da Silva
* **Contexto:** [N2-DOC-01] Passo 02 e Critério C3 (20% da N2)

---

## 1. Contexto e Problema

O Sistema de Geração e Correção Automática de Avaliações (SGP) possui como requisito central a correção automática de folhas de resposta impressas a partir de fotos tiradas por smartphone ou digitalizações por scanner.

Esse processo envolve desafios técnicos críticos:
* As fotos enviadas pelos professores podem apresentar variações angulares (perspectiva inclinada), iluminação heterogênea, pequenas sombras ou distorções de escala.
* É mandatório identificar a versão específica da avaliação (ex: Versão A, B ou C) para carregar o gabarito correspondente.
* As bolhas preenchidas pelos estudantes variam em intensidade (lápis grafite claro, caneta preta ou azul), exigindo um algoritmo com tolerância a ruído, capacidade de detectar dupla marcação (anulação) e marcação em branco.

Necessitava-se de um ecossistema tecnológico maduro, confiável e com alta eficiência de processamento para realizar essas operações de visão computacional.

---

## 2. Decisão Arquitetural

Decidiu-se adotar **Python 3.11** como a linguagem base do módulo de Visão Computacional / OMR, integrando as seguintes bibliotecas:
1. **OpenCV (`opencv-python-headless`):** Para todo o pipeline de processamento digital de imagem:
   * Conversão de espaço de cores (`cv2.cvtColor` para grayscale).
   * Redução de ruídos através de filtro gaussiano (`cv2.GaussianBlur`).
   * Binarização adaptativa pelo método de Otsu (`cv2.threshold`), que encontra automaticamente o limiar ideal para separar grafite/tinta do papel branco.
   * Detecção de contornos e cantoneiras de alinhamento (`cv2.findContours` e `cv2.approxPolyDP`).
   * Correção geométrica de perspectiva em 4 pontos (`cv2.getPerspectiveTransform` e `cv2.warpPerspective`).
2. **pyzbar:** Para localização e decodificação direta do QR Code de versão inserido na folha de respostas.
3. **NumPy:** Para operações vetoriais de contagem de densidade de pixels nas regiões de interesse (ROIs) de cada alternativa.

---

## 3. Alternativas Avaliadas

### Alternativa A: Bibliotecas OMR em JavaScript / Node.js (ex: Tesseract.js, Jimp, OpenCV.js)
* **Pontos Negativos:** O ecossistema Node.js é limitado para visão computacional clássica. O `Tesseract.js` é focado em OCR de texto corrido (e não em segmentação geométrica de marcas/bolhas), sendo extremamente lento. O `OpenCV.js` em ambiente servidor (Node.js) apresenta wrappers instáveis e consumo elevado de memória.

### Alternativa B: Serviços de OCR em Nuvem (Google Cloud Vision API, AWS Textract)
* **Pontos Negativos:** Custo recorrente por imagem processada, dependência obrigatória de conectividade com a internet de alta largura de banda para upload de imagens pesadas, latência de rede adicional e falta de algoritmos customizados para cálculo diferencial de densidade de bolhas adjacentes.

---

## 4. Consequências da Decisão

### Consequências Positivas:
* **Padrão da Indústria:** OpenCV é a biblioteca mais consolidada do mundo em visão computacional, com algoritmos otimizados em C/C++ por baixo do capô.
* **Custo Zero e Autonomia:** Processamento 100% local no servidor da aplicação, sem custos operacionais por avaliação corrigida.
* **Resiliência e Precisão:** A correção de perspectiva via cantoneiras garante que folhas fotografadas com pequenas inclinações sejam normalizadas perfeitamente antes da contagem de pixels.
* **Geração de Imagens de Auditoria:** O OpenCV permite desenhar os contornos das bolhas identificadas (verde para acerto, vermelho para erro), gerando um arquivo de imagem com feedback visual completo para o professor.

### Consequências Negativas e Mitigações:
* **Uso de CPU:** Processamento intensivo de matrizes.  
  * *Mitigação:* As imagens recebidas são redimensionadas para largura máxima de 1600px antes do processamento, mantendo o tempo médio por folha abaixo de 800ms.
* **Dependência do Sistema Operacional:** O `pyzbar` depende da biblioteca nativa `libzbar0`.  
  * *Mitigação:* Dependência devidamente mapeada no `Dockerfile` e no guia de instalação do projeto.
