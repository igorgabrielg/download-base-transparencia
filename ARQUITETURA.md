# Arquitetura do Sistema — Download Base Transparencia

---

## DESCRICAO DO PROJETO

Sistema em Python + React para download massivo e automatizado de dados abertos do Portal da Transparencia do Governo Federal do Brasil. Consome APIs REST de Despesas e Receitas com gerenciamento de multiplos tokens, rotacao inteligente e controle rigoroso de rate limit por janela de 60 segundos.

**Problema resolvido:**
- Limites de requisicao por token tornam download manual inviavel em larga escala
- Complexidade de gerenciar multiplos tokens, janelas de tempo e paginacao
- Perda de dados por falta de salvamento incremental e controle de checkpoints

**Publico-alvo:** Estudantes de graduacao (TCC) e pos-graduacao que precisam de bases de despesas/receitas federais para analises quantitativas.

---

## DEFINICAO DO AGENTE

**Nivel de autoridade: `controlled`**

A IA que executara as tarefas deste projeto opera com as seguintes restricoes:

- **Execucao mediante aprovacao:** apresentar plano de acao antes de modificar codigo; aguardar confirmacao
- **Criacao de arquivos:** permitida apenas apos confirmacao explicita
- **Comandos destrutivos:** proibidos sem aprovacao (delete, overwrite, force push)
- **Instalacao de dependencias:** apresentar lista e aguardar aprovacao antes de `pip install` ou `npm install`
- **Decisoes de arquitetura:** propor alternativas com justificativas; decisao final do usuario
- **Refatoracoes:** somente quando solicitadas
- **Testes:** pode executar automaticamente, mas nao alterar testes existentes sem aprovacao
- **Git:** commits locais permitidos; push/merge requer aprovacao explicita

---

## OBJETIVO GERAL

Fornecer uma ferramenta plug-and-play para pesquisadores baixarem dados do Portal da Transparencia de forma automatizada, maximizando throughput legal com rotacao de 3 tokens, salvamento incremental e zero perda de dados.

---

## NIVEL DE AUTONOMIA (do projeto gerado)

**Nivel: `controlled`**

- A IA deve sempre apresentar o plano antes de executar
- Confirmacao explicita necessaria para acoes que criam/modificam/deletam arquivos
- Instalacao de pacotes requer aprovacao previa
- Push/merge requer aprovacao explicita
- Pode executar testes e linters sem pedir permissao

---

## STACK BASE

### Backend
| Tecnologia | Versao |
|---|---|
| Python | 3.12+ |
| FastAPI | 0.115+ |
| Uvicorn | 0.34+ |
| httpx | 0.28+ |
| Pydantic | 2.10+ |
| pandas | 2.2+ |
| pytz | 2024.2+ |
| python-dotenv | 1.1+ |
| websockets | 15.0+ |

### Frontend
| Tecnologia | Versao |
|---|---|
| React | 19+ |
| TypeScript | 5.6+ |
| Vite | 6+ |
| TailwindCSS | 4+ |
| React Router | 7+ |
| Recharts | 2.15+ |
| Lucide React | 0.470+ |
| Axios | 1.7+ |
| @tanstack/react-query | 5.67+ |

### Complementares
- **Backend:** uuid, logging, pathlib (stdlib), python-dotenv
- **Frontend:** clsx, tailwind-merge, react-hot-toast

---

## REQUISITOS E INTERFACES

### Funcionalidades

| # | Nome | Prioridade |
|---|------|------------|
| F01 | Cadastro de Tokens (ate 3, com validacao online) | Alta |
| F02 | Validacao de Token Online | Alta |
| F03 | Definicao de Periodo (2004-2026, ano/mes) | Alta |
| F04 | Configuracao de Rate Limit (madrugada/dia/restrita) | Alta |
| F05 | Selecao de Endpoints (despesas/receitas) | Alta |
| F06 | Configuracao de Saida (diretorio, formato CSV, modo escrita) | Alta |
| F07 | Execucao de Download (iniciar/pausar/retomar/parar) | Alta |
| F08 | Rotacao Automatica de Tokens | Alta |
| F09 | Monitoramento de Tokens (status, contadores, reset) | Media |
| F10 | Paginacao Automatica | Alta |
| F11 | Salvamento Incremental CSV | Alta |
| F12 | Visualizacao de Logs (filtros por data, nivel, endpoint) | Media |
| F13 | Progresso de Downloads (grid ano/mes/endpoint) | Media |
| F14 | Retomada de Download (a partir de checkpoint) | Alta |
| F15 | Rate Limit Adaptativo por horario (Brasilia) | Alta |
| F16 | Tratamento de Erros HTTP (429/401/5xx/timeout) | Alta |

### Regras de Negocio Principais

| # | Regra |
|---|-------|
| RN01 | Pelo menos 1 token obrigatorio |
| RN02 | Token duplicado nao permitido |
| RN03 | Pelo menos 1 endpoint selecionado |
| RN04 | `ano_fim >= ano_inicio` |
| RN05 | Se mesmo ano, `mes_fim >= mes_inicio` |
| RN06 | Madrugada (00h-06h): aplica `max_req_madrugada` |
| RN07 | Dia (06h-24h): aplica `max_req_dia` |
| RN08 | Cada token com contador independente por janela 60s |
| RN09 | Todos tokens no limite → aguarda reset da janela mais proxima |
| RN10 | HTTP 429 → marca token "limite atingido", rotaciona |
| RN11 | HTTP 401 → marca token "invalido", remove da fila |
| RN12 | HTTP 5xx/timeout → retry ate 3x com backoff (2s, 4s, 8s) |
| RN13 | Lista vazia = fim da paginacao do periodo |
| RN14 | Checkpoint salvo apos cada pagina com sucesso |
| RN15 | Diretorios criados automaticamente se inexistentes |
| RN16 | Busca em logs exige minimo 3 caracteres |
| RN17 | Configuracoes persistidas entre sessoes (JSON) |

### Estrutura de Dados

**config.json** — Configuracao centralizada (tokens, periodo, rate limits, endpoints, diretorios, formato saida)

**checkpoint.json** — Estado de progresso por endpoint/ano/mes/pagina com status (pendente/em_andamento/concluido/erro)

**logs.txt** — Registro estruturado: timestamp, nivel, token_id, endpoint, ano, mes, pagina, status_http, mensagem

**token_status (runtime)** — Estado em memoria: status do token, req/min atual, limite aplicavel, janela inicio, tempo para reset

**download_progress (derivado)** — Visao consolidada de progresso derivada dos checkpoints

### Interfaces (10 Telas)

| Rota | Tela | Descricao |
|------|------|-----------|
| `/config/tokens` | Configuracao de Tokens | Cadastro e validacao de ate 3 tokens |
| `/config/periodo` | Configuracao de Periodo | Intervalo ano/mes para download |
| `/config/rate-limit` | Configuracao de Rate Limit | Limites por faixa horaria, fuso, tamanho pagina |
| `/config/endpoints` | Selecao de Endpoints | Despesas/receitas, URL base |
| `/config/saida` | Configuracao de Saida | Diretorio, formato nome, modo escrita |
| `/execucao` | Painel de Execucao | Controle principal com metricas em tempo real |
| `/monitor/tokens` | Monitor de Tokens | Cards com status, barra progresso, countdown |
| `/logs` | Visualizador de Logs | Tabela filtrada com exportacao |
| `/progresso` | Progresso de Downloads | Grid calendario (anos x meses) com cores |
| `/retomada` | Retomada de Download | Form + tabela de checkpoints |

### Validacoes Principais

- **Tokens:** token_1 obrigatorio, sem duplicatas, validacao opcional via API
- **Periodo:** ano 2004-2026, mes 1-12, cruzamento valido
- **Rate Limit:** madrugada max 700, dia max 400, restrita max 180, pagina 1-500
- **Endpoints:** pelo menos 1 selecionado, URL valida
- **Saida:** caminhos validos, formato `por_ano_mes`/`por_ano`, modo `append`/`overwrite`

---

## DESIGN E UX

### Identidade Visual

**Paleta Light:**
- Primaria: `#1a1a1a` | Destaque: `#3b82f6` | Fundo: `#ffffff` | Borda: `#e5e5e5`

**Cores Semanticas:** Success `#22c55e` | Warning `#eab308` | Error `#ef4444` | Info `#3b82f6` | Orange `#f97316`

**Dark Mode:**
- Fundo: `#0a0a0a` | Superficie 1: `#171717` | Superficie 2: `#262626` | Texto: `#fafafa` | Destaque: `#60a5fa`
- Transicao: `background-color 200ms, color 200ms`

### Tipografia
- **Corpo:** Inter | **Dados/Logs/Tokens:** JetBrains Mono
- Body: 14px/400 | h1: 28px/700 | h2: 22px/600 | Mono: 13px/400

### Layout
- Container max-width: `1200px`, centrado
- Sidebar fixa esquerda (240px) + area conteudo direita
- Espacamento base: 4px (escala: 4, 8, 12, 16, 24, 32, 48, 64)
- Border-radius: 8px (cards), 6px (inputs/botoes), 4px (badges)

### Responsividade
| Breakpoint | Comportamento |
|------------|--------------|
| >= 1024px | Sidebar visivel, grids multi-coluna |
| 768-1023px | Sidebar colapsavel, grids 2 colunas |
| < 768px | Sidebar drawer, single column, tabelas scroll horizontal |

### Tom de Voz
- Profissional, direto, tecnico sem intimidar
- Sucesso: "Configuracao salva com sucesso."
- Erro: "Informe pelo menos um token valido."
- Rate limit: "Token 1 atingiu o limite. Alternando para Token 2."

### Layouts por Tela
- **Configs** (`/config/*`): single column, max 640px, form empilhado
- **Execucao**: grid 2 colunas — metricas (esquerda) + console logs tempo real (direita, fundo escuro mono)
- **Monitor Tokens**: grid 3 colunas (1 card/token) com badge status, barra progresso, countdown
- **Logs**: filtros horizontal + tabela zebrada com paginacao
- **Progresso**: grid calendario 12 colunas (meses) x N linhas (anos), celulas coloridas por status
- **Retomada**: split form + tabela checkpoints

---

## INFRAESTRUTURA E DEVOPS

### Repositorio Git
- **Plataforma:** GitHub (privado)
- **Branches:** `main` (protegida) → `develop` → `feature/*`, `fix/*`, `release/*`
- **Commits:** Conventional Commits (`feat`, `fix`, `docs`, `chore`, `ci`)

### CI/CD (GitHub Actions)
- **Stages:** lint → test → build
- **Backend:** ruff check + format, pytest
- **Frontend:** tsc --noEmit, npm run build
- **Pre-commit:** ruff, trailing-whitespace, end-of-file-fixer, check-yaml, no-commit-to-branch main

### Deploy
- **Modelo:** Execucao local (maquina do pesquisador)
- **Ambientes:** development (hot reload, debug) / production (build otimizado, uvicorn)
- **Scripts:** `scripts/setup.sh`, `scripts/dev.sh`, `scripts/start.sh`
- **Makefile:** `make setup`, `make dev`, `make start`, `make test`, `make lint`

### Monitoramento
- Logging nativo: `logs/app.log` + stdout
- Health checks: `GET /api/health` (config, dirs) + `GET /api/health/api` (conectividade Portal)
- Alertas via WebSocket + toast no frontend (tokens em limite, token invalido, retries falhados, disco < 500MB, download concluido)

### Estrutura de Pastas

```
download-base-transparencia/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/ (schemas.py, checkpoint.py)
│   │   ├── routers/ (config_router, download_router, logs_router, progress_router)
│   │   ├── services/ (downloader, token_manager, csv_writer, checkpoint_service, log_service)
│   │   ├── core/ (rate_limiter, websocket)
│   │   └── utils/ (timezone)
│   ├── data/
│   ├── logs/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/ (client.ts, endpoints.ts)
│   │   ├── hooks/ (useConfig, useDownload, useWebSocket, useLogs)
│   │   ├── pages/ (10 paginas)
│   │   ├── components/ (layout/ + ui/)
│   │   ├── styles/
│   │   └── types/
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── scripts/ (setup.sh, dev.sh, start.sh)
├── Makefile
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── .gitignore
└── README.md
```

### Integracao Frontend-Backend
- **Proxy Vite:** `/api` → `localhost:8000`, `/ws` → WebSocket
- **Cliente HTTP:** Axios com baseURL `/api`, timeout 10s
- **Estado:** @tanstack/react-query para cache e refetch
- **Tempo real:** WebSocket em `ws://localhost:8000/ws/status` com reconexao automatica

### Variaveis de Ambiente (.env)
```
APP_ENV, APP_HOST, APP_PORT
TOKEN_1, TOKEN_2, TOKEN_3
API_BASE_URL, MAX_REQ_MADRUGADA, MAX_REQ_DIA, MAX_REQ_RESTRITA
ANO_INICIO, ANO_FIM, DIRETORIO_SAIDA, DIRETORIO_LOGS, FUSO_HORARIO
VITE_API_URL, VITE_WS_URL
```

### Padroes de Codigo
- **Python:** snake_case (arquivos, funcoes), PascalCase (classes)
- **TypeScript:** PascalCase (componentes), camelCase (funcoes/vars), `use` prefix (hooks)
- **Rotas API:** kebab-case
- **Imports:** stdlib → terceiros → locais (Python); react → libs → components → hooks → types (TS)

---

## CRITERIOS DE SUCESSO

| # | Criterio | Metrica |
|---|----------|---------|
| 1 | Nenhum bloqueio por rate limit | Zero HTTP 429 nao recuperados |
| 2 | Cobertura temporal completa | 100% dos meses/anos configurados possuem CSV |
| 3 | Integridade dos dados | Nenhuma pagina perdida ou duplicada |
| 4 | Throughput efetivo | >= 90% do limite seguro utilizado |
| 5 | Recuperacao de falhas | Retomada sem reprocessar paginas ja salvas |
| 6 | Logs auditaveis | 100% das requisicoes registradas com campos completos |
| 7 | Tempo de setup < 5 min | Usuario configura e executa rapidamente |
| 8 | Execucao sem intervencao | Download completo de 1 ano sem acao manual |

---

## CONDICAO DE PARADA

- Todos os criterios de sucesso atendidos
- Todas as 16 funcionalidades implementadas e funcionais
- 10 telas do frontend operacionais com comunicacao backend via API/WebSocket
- CI/CD pipeline funcional (lint + test + build passando)
- Ou bloqueio explicito aguardando decisao do usuario
