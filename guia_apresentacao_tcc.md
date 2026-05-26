# Guia de Apresentação de TCC: Auditoria Orçamentária Cognitiva com Multiagentes e RAG

Este documento serve como roteiro técnico de apoio para a apresentação de resultados preliminares. Ele detalha o funcionamento técnico das **5 Etapas do Pipeline**, os resultados consolidados obtidos e as perguntas recomendadas organizadas por tópicos para a demonstração prática da banca examinadora.

---

## 1. Funcionamento das 5 Etapas do Sistema

O sistema foi arquitetado como uma infraestrutura de processamento de dados e inteligência artificial distribuída, dividida em 5 etapas sequenciais:

```
[Etapa 1] Normalização/Enriquecimento (CSVs -> JSON/SQLite)
     │
[Etapa 2] Análise Cognitiva Distribuída (Pareceres de IA)
     │
[Etapa 3] Síntese e Consolidação (Auditor-Chefe -> Relatório Geral)
     │
[Etapa 4] Indexação Vetorial Dinâmica (Top UGs/Métricas -> ChromaDB)
     │
[Etapa 5] Chat de Auditoria Inteligente (RAG Híbrido Ativo)
```

### Etapa 1: Extração, Normalização e Enriquecimento
*   **O que faz:** Lê as bases brutas do Portal da Transparência do Governo Federal (CSVs de receitas e despesas com milhões de registros).
*   **Processamento:**
    *   Padroniza tipos de dados, colunas e remove inconsistências.
    *   Constrói dicionários institucionais dinâmicos de Ministérios e Unidades Gestoras (UGs) em arquivos JSON para dar significado ao código SIAFI.
    *   Calcula de antemão métricas brutas agregadas (total gasto, total planejado, UG líder de despesas) gerando os arquivos consolidados `despesas_enriquecida.json` e `receitas_enriquecida.json` de forma extremamente otimizada.
    *   Persiste os dados em um banco relacional local SQLite (`transparencia.db`).

### Etapa 2: Análise Cognitiva Distribuída (IA)
*   **O que faz:** Dispara em paralelo e de forma assíncrona dois Agentes Especialistas de IA de nível de auditor (Agente de Receitas e Agente de Despesas).
*   **Processamento:**
    *   Os agentes consomem as bases resumidas e consolidadas de receitas e despesas.
    *   Utilizam a CLI do Antigravity (`agy`) acionando o modelo `gemini-3.5-flash` local.
    *   Geram pareceres técnicos de auditoria específicos, salvando arquivos de checkpoint físico (`receita_analise_cognitiva.json` e `despesa_analise_cognitiva.json`).

### Etapa 3: Síntese e Consolidação (Auditor-Chefe)
*   **O que faz:** O Agente Redator (Auditor-Chefe de Estado) lê os pareceres técnicos gerados na Etapa 2 e consolida-os.
*   **Processamento:**
    *   Cruza dados de arrecadação global contra a execução de gastos do período.
    *   Dedica uma seção detalhada para analisar as **assimetrias orçamentárias** estruturais da União (por que órgãos como MEC, Saúde ou Defesa concentram recursos e outros menores possuem orçamento nulo).
    *   Classifica formalmente a conjuntura fiscal em *Positiva*, *Neutra* ou *Negativa* e grava o `relatorio_final_consolidado.txt` em Markdown.

### Etapa 4: Indexação Vetorial Dinâmica (ChromaDB)
*   **O que faz:** Prepara o motor de busca semântica para o Chat de Auditoria.
*   **Processamento:**
    *   Fragmenta o relatório consolidado geral do Auditor-Chefe em blocos de texto (chunks) com sobreposição inteligente.
    *   Lê os JSONs de despesas e receitas e calcula dinamicamente a **participação percentual (%)** de cada um dos 37 ministérios sobre o orçamento da União.
    *   Agrupa e calcula o **ranking de maiores UGs de despesa** (Top 5) de cada pasta.
    *   Cria e vetoriza fichas detalhadas de cada Ministério contendo esses dados no banco de dados vetorial local ChromaDB (`vector_store`).

### Etapa 5: Chat de Auditoria Inteligente (RAG Híbrido Ativo)
*   **O que faz:** A interface de conversação que responde às perguntas do auditor com precisão factual.
*   **Processamento:**
    *   Lê o relatório consolidado na íntegra de forma estática no prompt (garantindo que dados macro do governo nunca falhem na busca vetorial).
    *   Realiza a busca vetorial no ChromaDB trazendo as top 8 fichas/chunks específicos.
    *   Garante via prompt blindado que: se o dado não constar no CSV, responde *"não consta no CSV"*; se houver erro ou falta de dados para cálculo preciso, responde a frase de erro padrão pedindo novo processamento.

---

## 2. Resultados Consolidados do Período Auditado (Exemplo Prático)

Para a sua apresentação, estes são os grandes números gerados e auditados pelo sistema no último processamento:

*   **Receita Realizada Global:** R$ 5.614.085.003.109,29 (R$ 5,61 trilhões).
*   **Despesa Total Executada:** R$ 4.918.932.931.791,45 (R$ 4,92 trilhões).
*   **Frustração de Receitas:** R$ 106.176.094.460,01 (-1,86% do previsto atualizado).
*   **Maior Unidade Gestora em Despesas (Líder Geral):** Coordenação-Geral de Controle da Dívida Pública (COGEP - UG 170600), com R$ 2.127.695.030.497,72 liquidados (representando **43,26%** de todo o orçamento geral da União).
*   **Classificação Fiscal:** Negativa (decorrente da altíssima rigidez orçamentária para pagamento da dívida e a frustração de receitas assistenciais/previdenciárias).

---

## 3. Banco de Perguntas para Apresentação (Organizado por Tópicos)

Utilize estes tópicos e perguntas para demonstrar a robustez do sistema à banca:

### Tópico A: Visão Macro e Saúde Fiscal (Relatório Consolidado)
*   **Pergunta 1:** *"Qual o parecer conclusivo do Auditor-Chefe sobre a situação fiscal do período?"*
    *   *Foco da resposta:* Expor que a situação é classificada como Negativa, destacando a incompatibilidade estrutural e rigidez do serviço da dívida.
*   **Pergunta 2:** *"De quanto foi a receita realizada global comparada com a despesa total executada?"*
    *   *Foco da resposta:* Trazer os valores exatos na casa dos trilhões (R$ 5.61T vs R$ 4.92T) e explicar que o superávit aparente encobre a frustração de receitas previstas.

### Tópico B: Perfil e Peso dos Ministérios (Fichas Orçamentárias)
*   **Pergunta 3:** *"Qual é a participação percentual do Ministério da Educação (MEC) no gasto governamental total e na arrecadação?"*
    *   *Foco da resposta:* Trazer que o MEC gasta R$ 215.84B (4.39% do total do governo) e arrecada R$ 51.61B (0.92% do total do governo).
*   **Pergunta 4:** *"Qual o percentual do orçamento geral consumido pelo Ministério da Defesa?"*
    *   *Foco da resposta:* Demonstrar a participação de 2.56% (R$ 125.84 bilhões) consumidos pela pasta.

### Tópico C: Análise e Justificativa de Assimetria
*   **Pergunta 5:** *"Por que o Ministério da Previdência Social consome mais de 20% do orçamento total executado enquanto outros órgãos operam com dotações quase nulas?"*
    *   *Foco da resposta:* A IA explicará a natureza constitucional dos direitos adquiridos (Previdência consome R$ 1.10 trilhão, ou 22.33%) e justificará que órgãos menores operam apenas em escopo administrativo enxuto ou transferência descentralizada.

### Tópico D: Unidades Gestoras (UGs) de Despesa
*   **Pergunta 6:** *"Quais são as maiores Unidades Gestoras vinculadas ao Ministério da Educação e seus respectivos gastos?"*
    *   *Foco da resposta:* Trazer o ranking das UGs vinculadas (como FNDE liderando despesas em R$ 82.3B, seguido por UFPR, etc.).
*   **Pergunta 7:** *"Qual a UG que mais gasta no Ministério da Fazenda e qual a sua representatividade?"*
    *   *Foco da resposta:* Apontar a COGEP (UG 170600) com R$ 2.12 trilhões executados (79.57% do orçamento do Ministério da Fazenda).

### Tópico E: Robustez de Limites e Erros (Blindagem)
*   **Pergunta 8:** *"Qual foi o gasto da UG de Exploração Espacial da Amazônia?"*
    *   *Foco da resposta:* Provar a blindagem de alucinação. O chat responderá: *"A informação não consta no CSV."*
