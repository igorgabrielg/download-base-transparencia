# Download Base Transparência — Especificações Técnicas

---

## 1. Funcionalidades

| # | Nome | Descrição | Prioridade | Tela Relacionada |
|---|------|-----------|------------|------------------|
| F01 | Cadastro de Tokens | Cadastrar até 3 tokens da API do Portal da Transparência, com validação opcional contra a API antes de salvar | Alta | Configuração de Tokens |
| F02 | Validação de Token Online | Testar cada token informado realizando chamada real à API e retornando status (válido/inválido) | Alta | Configuração de Tokens |
| F03 | Definição de Período | Configurar intervalo de anos e meses para download dos dados (2004–2026) | Alta | Configuração de Período |
| F04 | Configuração de Rate Limit | Definir limites de requisições/minuto por faixa horária (madrugada, dia, restrita), fuso e tamanho de página | Alta | Configuração de Rate Limit |
| F05 | Seleção de Endpoints | Escolher quais APIs serão consumidas (despesas, receitas ou ambas) e definir URL base | Alta | Seleção de Endpoints |
| F06 | Configuração de Saída | Definir diretório de saída, formato de nomeação dos CSVs, modo de escrita e diretório de logs | Alta | Configuração de Saída |
| F07 | Execução de Download | Iniciar, pausar, retomar e parar o processo de download com feedback em tempo real | Alta | Painel de Execução |
| F08 | Rotação Automática de Tokens | Alternar entre tokens ativos quando um atinge o limite de requisições na janela de 60s | Alta | Monitor de Tokens |
| F09 | Monitoramento de Tokens | Exibir status, contadores e tempo para reset de cada token em tempo real | Média | Monitor de Tokens |
| F10 | Paginação Automática | Iterar páginas incrementalmente até esgotar dados de cada período/endpoint | Alta | Painel de Execução |
| F11 | Salvamento Incremental CSV | Persistir dados em CSV após cada página, com append ou overwrite conforme configurado | Alta | Configuração de Saída |
| F12 | Visualização de Logs | Consultar e filtrar logs por data, nível, endpoint, token e texto livre | Média | Visualizador de Logs |
| F13 | Progresso de Downloads | Exibir progresso geral por ano/mês/endpoint, com indicação de concluídos e pendentes | Média | Progresso de Downloads |
| F14 | Retomada de Download | Retomar downloads interrompidos a partir do último checkpoint salvo | Alta | Retomada de Download |
| F15 | Rate Limit Adaptativo | Detectar faixa horária atual (Brasília) e aplicar limite correspondente automaticamente | Alta | Configuração de Rate Limit |
| F16 | Tratamento de Erros HTTP | Retry com backoff em 500/timeout, troca de token em 429, skip de token em 401 | Alta | Painel de Execução |

---

## 2. Regras de Negócio

| # | Regra | Contexto | Validação |
|---|-------|----------|-----------|
| RN01 | Pelo menos 1 token deve ser cadastrado | Configuração de Tokens | Impedir salvamento sem token_1 preenchido |
| RN02 | Token duplicado não é permitido | Configuração de Tokens | Comparar valores dos 3 campos; rejeitar se houver iguais |
| RN03 | Pelo menos 1 endpoint deve ser selecionado | Seleção de Endpoints | `baixar_despesas OR baixar_receitas` deve ser true |
| RN04 | `ano_fim >= ano_inicio` | Configuração de Período | Rejeitar se ano_fim < ano_inicio |
| RN05 | Se `ano_inicio == ano_fim`, então `mes_fim >= mes_inicio` | Configuração de Período | Validar cruzamento de meses no mesmo ano |
| RN06 | Faixa horária madrugada: 00:00–05:59 (fuso configurado) → aplica `max_req_madrugada` | Execução | Sistema verifica hora atual a cada janela de 60s |
| RN07 | Faixa horária dia: 06:00–23:59 → aplica `max_req_dia` | Execução | Idem RN06 |
| RN08 | Cada token possui contador independente por janela de 60s | Execução | Contador reseta a cada 60s por token |
| RN09 | Quando todos os tokens atingem limite, sistema aguarda reset da janela mais próxima | Execução | Calcula menor tempo restante entre os tokens |
| RN10 | HTTP 429 → marca token como "limite atingido" e rotaciona para próximo | Execução | Registro em log + troca imediata |
| RN11 | HTTP 401 → marca token como "inválido" e não o reutiliza na sessão | Execução | Token removido da fila de rotação |
| RN12 | HTTP 5xx/timeout → retry até 3 vezes com backoff exponencial (2s, 4s, 8s) | Execução | Após 3 falhas consecutivas, registra erro e avança |
| RN13 | Página sem resultados (lista vazia) indica fim da paginação do período | Execução | Avança para próximo mês/endpoint |
| RN14 | Checkpoint salvo após cada página com sucesso (endpoint, ano, mês, página) | Execução | Persiste em arquivo de controle |
| RN15 | Diretórios de saída e logs devem ser criados automaticamente se não existirem | Configuração de Saída | `os.makedirs(path, exist_ok=True)` |
| RN16 | Busca de texto em logs exige mínimo 3 caracteres | Visualizador de Logs | Rejeitar busca com < 3 caracteres |
| RN17 | Configurações devem ser persistidas entre sessões | Todas as telas de configuração | Salvar em arquivo JSON/YAML no diretório do projeto |

---

## 3. Validações

### Configuração de Tokens

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| token_1 | string | Sim | Não vazio; formato alfanumérico; se `validar_tokens=true`, testar via GET na API |
| token_2 | string | Não | Mesmo formato de token_1; não pode ser igual a token_1 |
| token_3 | string | Não | Mesmo formato; não pode ser igual a token_1 ou token_2 |
| validar_tokens | boolean | Não | Default: false |

### Configuração de Período

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| ano_inicio | integer | Sim | 2004 ≤ valor ≤ 2026 |
| ano_fim | integer | Sim | ano_inicio ≤ valor ≤ 2026 |
| mes_inicio | integer (select) | Não | 1 ≤ valor ≤ 12; default: 1 |
| mes_fim | integer (select) | Não | 1 ≤ valor ≤ 12; default: 12; se mesmo ano, ≥ mes_inicio |

### Configuração de Rate Limit

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| max_req_madrugada | integer | Sim | 1 ≤ valor ≤ 700; default: 590 |
| max_req_dia | integer | Sim | 1 ≤ valor ≤ 400; default: 390 |
| max_req_restrita | integer | Sim | 1 ≤ valor ≤ 180; default: 170 |
| fuso_horario | string | Sim | Fuso válido via `pytz`/`zoneinfo`; default: America/Sao_Paulo |
| tamanho_pagina | integer | Sim | 1 ≤ valor ≤ 500; default: 500 |

### Seleção de Endpoints

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| baixar_despesas | boolean | Sim | Pelo menos um (despesas ou receitas) deve ser true |
| baixar_receitas | boolean | Sim | Idem |
| base_url | string | Sim | URL válida (regex ou urllib.parse); default: `https://api.portaldatransparencia.gov.br/api-de-dados` |

### Configuração de Saída

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| diretorio_saida | string | Sim | Caminho válido no SO; criado se inexistente |
| formato_nome_arquivo | string (select) | Sim | Valores: `por_ano_mes`, `por_ano` |
| modo_escrita | string (select) | Sim | Valores: `append`, `overwrite` |
| diretorio_logs | string | Sim | Caminho válido; default: mesmo que diretorio_saida |

### Retomada de Download

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| endpoint_retomada | string (select) | Sim | Valores: `despesas`, `receitas` |
| ano_retomada | integer | Sim | 2004 ≤ valor ≤ 2026 |
| mes_retomada | integer (select) | Sim | 1 ≤ valor ≤ 12 |
| pagina_retomada | integer | Sim | ≥ 1 |
| ignorar_arquivos_existentes | boolean | Não | Default: false |

### Visualizador de Logs

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| filtro_data_inicio | date | Não | Formato YYYY-MM-DD |
| filtro_data_fim | date | Não | ≥ filtro_data_inicio |
| filtro_nivel_log | string (select) | Não | Valores: `todos`, `info`, `warning`, `error` |
| filtro_endpoint | string (select) | Não | Valores: `todos`, `despesas`, `receitas` |
| filtro_token | string (select) | Não | Valores: `todos`, `token_1`, `token_2`, `token_3` |
| busca_texto | string | Não | Mínimo 3 caracteres se preenchido |

### Progresso de Downloads

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| filtro_ano | integer | Não | Entre ano_inicio e ano_fim configurados |
| filtro_endpoint | string (select) | Não | Valores: `todos`, `despesas`, `receitas` |
| exibir_apenas_pendentes | boolean | Não | Default: false |

---

## 4. Estrutura de Dados

> **Nota:** O projeto não utiliza banco de dados relacional. Os dados são persistidos em arquivos JSON (configurações e checkpoints) e CSV (dados baixados). As "tabelas" abaixo representam as estruturas lógicas dos arquivos.

### 4.1 config (arquivo `config.json`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador da configuração |
| token_1 | string | Token principal (obrigatório) |
| token_2 | string | Token secundário |
| token_3 | string | Token terciário |
| ano_inicio | integer | Ano inicial do download |
| ano_fim | integer | Ano final do download |
| mes_inicio | integer | Mês inicial (default 1) |
| mes_fim | integer | Mês final (default 12) |
| max_req_madrugada | integer | Limite req/min 00h–06h |
| max_req_dia | integer | Limite req/min 06h–24h |
| max_req_restrita | integer | Limite req/min APIs restritas |
| fuso_horario | string | Fuso horário |
| tamanho_pagina | integer | Registros por página |
| baixar_despesas | boolean | Baixar endpoint despesas |
| baixar_receitas | boolean | Baixar endpoint receitas |
| base_url | string | URL base da API |
| diretorio_saida | string | Caminho de saída dos CSVs |
| formato_nome_arquivo | string | `por_ano_mes` ou `por_ano` |
| modo_escrita | string | `append` ou `overwrite` |
| diretorio_logs | string | Caminho dos logs |
| active | boolean | Configuração ativa |
| created_at | timestamp | Data de criação |
| last_update | timestamp | Última atualização |

### 4.2 checkpoint (arquivo `checkpoint.json`)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador do checkpoint |
| endpoint | string | `despesas` ou `receitas` |
| ano | integer | Ano sendo processado |
| mes | integer | Mês sendo processado |
| pagina | integer | Última página salva com sucesso |
| total_registros | integer | Total de registros baixados neste período |
| status | string | `pendente`, `em_andamento`, `concluido`, `erro` |
| arquivo_csv | string | Nome do arquivo CSV gerado |
| active | boolean | Registro ativo |
| created_at | timestamp | Data de criação |
| last_update | timestamp | Última atualização |

### 4.3 log_entry (arquivo `logs.txt` / estrutura lógica)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador do log |
| timestamp | timestamp | Data/hora do evento |
| nivel | string | `info`, `warning`, `error` |
| token_id | string | Token utilizado (`token_1`, `token_2`, `token_3`) |
| endpoint | string | `despesas` ou `receitas` |
| ano | integer | Ano da requisição |
| mes | integer | Mês da requisição |
| pagina | integer | Página requisitada |
| status_http | integer | Código HTTP da resposta |
| mensagem | string | Descrição do evento |
| registros_obtidos | integer | Qtd de registros na resposta |
| active | boolean | Registro ativo |
| created_at | timestamp | Data de criação |
| last_update | timestamp | Última atualização |

### 4.4 token_status (em memória / runtime)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador |
| token_id | string | `token_1`, `token_2`, `token_3` |
| status | string | `ativo`, `em_espera`, `invalido`, `limite_atingido` |
| req_minuto_atual | integer | Requisições feitas na janela atual |
| limite_aplicavel | integer | Limite vigente (baseado no horário) |
| janela_inicio | timestamp | Início da janela de 60s |
| tempo_para_reset | integer | Segundos restantes na janela |
| active | boolean | Token ativo |
| created_at | timestamp | Criação |
| last_update | timestamp | Última atualização |

### 4.5 download_progress (derivado de checkpoints)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador |
| endpoint | string | `despesas` ou `receitas` |
| ano | integer | Ano |
| mes | integer | Mês |
| status | string | `pendente`, `concluido`, `erro` |
| arquivo_csv | string | Arquivo gerado |
| tamanho_arquivo | integer | Tamanho em bytes |
| total_registros | integer | Registros baixados |
| active | boolean | Ativo |
| created_at | timestamp | Criação |
| last_update | timestamp | Atualização |

---

## 5. Interfaces

### 5.1 Configuração de Tokens

- **Rota:** `/config/tokens`
- **Objetivo:** Cadastrar e gerenciar tokens de acesso à API
- **Elementos de UI:**
  - Input text para `token_1` (com máscara parcial para segurança)
  - Input text para `token_2`
  - Input text para `token_3`
  - Checkbox `validar_tokens`
  - Botão "Validar" (testa tokens na API, exibe badge verde/vermelho por token)
  - Botão "Salvar"
  - Indicador visual de status por token (válido/inválido/não testado)
- **Ações:** Salvar, Validar, Limpar
- **Regras aplicáveis:** RN01, RN02

### 5.2 Configuração de Período

- **Rota:** `/config/periodo`
- **Objetivo:** Definir intervalo temporal para download
- **Elementos de UI:**
  - Input number `ano_inicio` (spinner, min 2004, max 2026)
  - Input number `ano_fim` (spinner, min dinâmico = ano_inicio)
  - Select `mes_inicio` (1–12)
  - Select `mes_fim` (1–12)
  - Label informativo: "Total de meses a processar: X"
  - Botão "Salvar"
- **Ações:** Salvar
- **Regras aplicáveis:** RN04, RN05

### 5.3 Configuração de Rate Limit

- **Rota:** `/config/rate-limit`
- **Objetivo:** Definir limites de requisições por faixa horária
- **Elementos de UI:**
  - Input number `max_req_madrugada` (slider ou spinner, max 700)
  - Input number `max_req_dia` (max 400)
  - Input number `max_req_restrita` (max 180)
  - Select `fuso_horario` (lista de fusos brasileiros)
  - Input number `tamanho_pagina` (1–500)
  - Tabela resumo das faixas horárias com limites configurados
  - Botão "Salvar"
- **Ações:** Salvar, Restaurar Padrões
- **Regras aplicáveis:** RN06, RN07

### 5.4 Seleção de Endpoints

- **Rota:** `/config/endpoints`
- **Objetivo:** Selecionar APIs a serem consultadas
- **Elementos de UI:**
  - Checkbox `baixar_despesas`
  - Checkbox `baixar_receitas`
  - Input text `base_url` (com botão de teste de conectividade)
  - Mensagem de erro se nenhum endpoint selecionado
  - Botão "Salvar"
- **Ações:** Salvar, Testar Conexão
- **Regras aplicáveis:** RN03

### 5.5 Configuração de Saída

- **Rota:** `/config/saida`
- **Objetivo:** Definir onde e como os arquivos serão salvos
- **Elementos de UI:**
  - Input text `diretorio_saida` (com botão browse/seletor de diretório)
  - Select `formato_nome_arquivo` (`por_ano_mes` / `por_ano`)
  - Select `modo_escrita` (`append` / `overwrite`)
  - Input text `diretorio_logs`
  - Preview do nome de arquivo gerado (ex: `despesas_2014_01.csv`)
  - Botão "Salvar"
- **Ações:** Salvar, Verificar Permissões do Diretório
- **Regras aplicáveis:** RN15

### 5.6 Painel de Execução

- **Rota:** `/execucao`
- **Objetivo:** Tela principal de controle e monitoramento do download em tempo real
- **Elementos de UI:**
  - Badge `status_execucao` (cores: verde=execução, amarelo=pausado, cinza=parado, vermelho=erro, azul=concluído)
  - Label `token_ativo`
  - Gauge/contador `requisicoes_no_minuto` (com barra visual do limite)
  - Label `endpoint_atual`
  - Label `ano_mes_atual`
  - Label `pagina_atual`
  - Contador `total_registros_baixados`
  - Botões: "Iniciar", "Pausar", "Retomar", "Parar"
  - Console de últimas mensagens de log (streaming)
- **Ações:** Iniciar Download, Pausar, Retomar, Parar
- **Regras aplicáveis:** RN06, RN07, RN08, RN09, RN10, RN11, RN12, RN13, RN14

### 5.7 Monitor de Tokens

- **Rota:** `/monitor/tokens`
- **Objetivo:** Acompanhar uso e status de cada token em tempo real
- **Elementos de UI:**
  - Card por token contendo:
    - `token_id` (label)
    - Badge `status_token` (ativo=verde, em_espera=amarelo, inválido=vermelho, limite_atingido=laranja)
    - Barra de progresso `requisicoes_minuto_atual` / `limite_aplicavel`
    - Countdown `tempo_para_reset` (segundos)
  - Indicador de faixa horária ativa e limite vigente
- **Ações:** Visualização apenas (somente leitura)
- **Regras aplicáveis:** RN08, RN09, RN10, RN11

### 5.8 Visualizador de Logs

- **Rota:** `/logs`
- **Objetivo:** Consultar e filtrar logs de execução
- **Elementos de UI:**
  - Filtros em barra superior:
    - Datepicker `filtro_data_inicio`
    - Datepicker `filtro_data_fim`
    - Select `filtro_nivel_log`
    - Select `filtro_endpoint`
    - Select `filtro_token`
    - Input text `busca_texto`
    - Botão "Filtrar"
  - Tabela de logs com colunas: timestamp, nível, token, endpoint, ano/mês, página, status HTTP, mensagem
  - Paginação da tabela
  - Botão "Exportar Logs" (CSV)
- **Ações:** Filtrar, Limpar Filtros, Exportar
- **Regras aplicáveis:** RN16

### 5.9 Progresso de Downloads

- **Rota:** `/progresso`
- **Objetivo:** Visão geral do progresso por ano/mês/endpoint
- **Elementos de UI:**
  - Filtros: `filtro_ano`, `filtro_endpoint`, `exibir_apenas_pendentes`
  - Grid/tabela tipo calendário: linhas = anos, colunas = meses (1–12)
    - Cada célula com cor: verde=concluído, cinza=pendente, vermelho=erro, azul=em andamento
    - Separação visual por endpoint (despesas/receitas)
  - Rodapé com totais:
    - `total_arquivos_gerados`
    - `tamanho_total_disco`
  - Barra de progresso geral (% concluído)
- **Ações:** Filtrar, Atualizar
- **Regras aplicáveis:** RN13, RN14

### 5.10 Retomada de Download

- **Rota:** `/retomada`
- **Objetivo:** Retomar downloads interrompidos a partir do último checkpoint
- **Elementos de UI:**
  - Select `endpoint_retomada`
  - Input number `ano_retomada`
  - Select `mes_retomada` (1–12)
  - Input number `pagina_retomada`
  - Checkbox `ignorar_arquivos_existentes`
  - Tabela de checkpoints salvos (últimos pontos de interrupção detectados) com botão "Usar" para preencher campos automaticamente
  - Botão "Iniciar Retomada"
- **Ações:** Preencher a partir de checkpoint, Iniciar Retomada
- **Regras aplicáveis:** RN14, RN15

---

*Documento gerado pelo Agente REQUISITOS — Sistema Arquiteto de Software*