# Download Base Transparência

## 1. Descrição do Sistema

O **Download Base Transparência** é um sistema em Python para download massivo e automatizado de dados abertos do Portal da Transparência do Governo Federal do Brasil. Ele consome as APIs REST de Despesas e Receitas, gerenciando múltiplos tokens de acesso com rotação inteligente e controle rigoroso de rate limit por janela de 60 segundos, garantindo máxima vazão sem violação dos limites da API.

O sistema opera com arquitetura assíncrona (asyncio), alternando automaticamente entre três tokens independentes, cada um com seu próprio contador de requisições. Detecta o fuso horário de Brasília para aplicar os limites corretos (madrugada vs. dia), pagina automaticamente todos os endpoints e persiste os resultados incrementalmente em arquivos CSV organizados por ano e mês.

Projetado para rodar de forma autônoma por longos períodos, o sistema é capaz de baixar milhões de registros sem bloqueio, com tratamento robusto de erros (retry, troca de token em 429, skip de token inválido) e logging completo de todas as operações.

## 2. Problema que Resolve

- **Acesso difícil a dados em larga escala**: o Portal da Transparência impõe limites de requisição por token, tornando o download manual ou com scripts simples extremamente lento e sujeito a bloqueios.
- **Complexidade de gerenciamento de tokens e rate limits**: controlar múltiplos tokens, respeitar janelas de tempo variáveis por horário e paginar milhares de páginas exige lógica não trivial que o sistema abstrai completamente.
- **Perda de dados e retrabalho**: sem controle de paginação e salvamento incremental, falhas durante o download forçam reinício do zero. O sistema garante persistência contínua e retomada segura.

## 3. Público-Alvo

- **Estudantes de graduação (TCC)**: que precisam de bases de dados de despesas e receitas federais para análises quantitativas, visualizações e trabalhos acadêmicos.
- **Estudantes de pós-graduação (mestrado/doutorado)**: pesquisadores que necessitam de séries históricas completas (2014–2026) para estudos em políticas públicas, ciência de dados ou economia.
- **Perfil técnico mínimo**: usuários com conhecimento básico de Python, capazes de configurar tokens e executar scripts via terminal.

## 4. Funcionalidades Principais

| Funcionalidade | Descrição |
|---|---|
| **Rotação automática de tokens** | Alterna entre 3 tokens com contadores independentes por janela de 60s. Quando todos atingem o limite, aguarda o reset da janela. |
| **Rate limit adaptativo por horário** | Detecta horário de Brasília (America/Sao_Paulo) e aplica limites seguros: 590 req/min (00h–06h), 390 req/min (06h–24h), 170 req/min (APIs restritas). |
| **Download de Despesas e Receitas** | Consome os endpoints `/despesas` e `/receitas` com paginação completa, iterando por ano (2014–2026) e mês (1–12). |
| **Paginação automática** | Loop incremental de páginas com `tamanhoPagina` máximo até esgotar os dados do período. |
| **Salvamento incremental em CSV** | Grava dados via pandas em arquivos nomeados por padrão (`despesas_2014_01.csv`, `receitas_2014.csv`), com append se o arquivo já existir. |
| **Tratamento robusto de erros** | HTTP 429 → troca token; 401 → pula token; 500/timeout → retry automático com backoff. |
| **Motor assíncrono (asyncio)** | Fila de requisições com `requests.Session` e controle central de rate limit para máxima vazão. |
| **Logging completo** | Registra em `logs.txt`: timestamp, token usado, endpoint, página, status HTTP e erros. |
| **Configuração centralizada** | Arquivo `config.py` com todos os parâmetros editáveis: tokens, intervalo de anos, limites, diretório de saída, URL base. |

## 5. Proposta de Valor

- **Plug-and-play para pesquisadores**: basta inserir 3 tokens gratuitos do Portal da Transparência e executar — o sistema faz o resto.
- **Maximiza throughput legal**: com 3 tokens e rotação inteligente, atinge até ~1.170 req/min na madrugada (3×390 de dia), extraindo dados na velocidade máxima permitida.
- **Zero perda de dados**: salvamento incremental + controle de página garante que nenhum registro é perdido ou duplicado, mesmo em caso de falha ou interrupção.
- **Gratuito e autocontido**: sem dependência de serviços pagos, bancos de dados externos ou infraestrutura cloud — roda em qualquer máquina com Python 3.

## 6. Critérios de Sucesso

| # | Critério | Métrica |
|---|---|---|
| 1 | **Nenhum bloqueio por rate limit** | Zero respostas HTTP 429 não recuperadas durante execução completa |
| 2 | **Cobertura temporal completa** | 100% dos meses/anos do intervalo configurado possuem CSV gerado |
| 3 | **Integridade dos dados** | Nenhuma página perdida ou duplicada — total de registros bate com paginação reportada |
| 4 | **Throughput efetivo** | ≥ 90% do limite seguro configurado é utilizado (sem ociosidade desnecessária) |
| 5 | **Recuperação de falhas** | Sistema retoma download após interrupção sem reprocessar páginas já salvas |
| 6 | **Logs auditáveis** | 100% das requisições registradas em `logs.txt` com todos os campos obrigatórios |
| 7 | **Tempo de setup < 5 min** | Usuário configura tokens e executa o sistema em menos de 5 minutos |
| 8 | **Execução sem intervenção** | Download completo de um ano inteiro (12 meses, 2 endpoints) sem necessidade de ação manual |