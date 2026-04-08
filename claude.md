# Download Base Transparencia

## Sobre o Projeto
Sistema Python + React para download massivo de dados do Portal da Transparencia (APIs de Despesas e Receitas). Gerencia multiplos tokens com rotacao inteligente, rate limit adaptativo por horario e salvamento incremental em CSV.

## Nivel de Autoridade da IA: CONTROLLED

### Execucao mediante aprovacao
- A IA DEVE apresentar o plano de acao ANTES de executar qualquer modificacao de codigo e aguardar confirmacao do usuario
- Toda criacao de arquivo requer confirmacao explicita
- Comandos destrutivos proibidos sem aprovacao (delete, overwrite, force push)

### Dependencias
- Apresentar lista completa de dependencias e aguardar aprovacao antes de executar `pip install` ou `npm install`

### Decisoes de arquitetura
- Propor alternativas e justificativas; decisao final e do usuario
- Refatoracoes somente quando solicitadas; nao refatorar proativamente

### Testes e qualidade
- Pode executar testes automaticamente (`make test`, `make lint`)
- NAO deve alterar testes existentes sem aprovacao

### Git
- Commits locais: permitido
- Push/merge: requer aprovacao explicita
- Force push: PROIBIDO sem aprovacao

### O que a IA pode fazer autonomamente
- Ler e analisar arquivos existentes
- Executar comandos read-only (lint, typecheck, build, test)
- Sugerir correcoes, melhorias e planos de acao

### O que a IA NAO deve fazer
- Push para repositorio sem aprovacao
- Modificar configuracoes de sistema
- Executar comandos destrutivos
- Alterar .env com dados sensiveis (tokens, credenciais)
- Deploy em producao

## Stack
- **Backend:** Python 3.12+, FastAPI, httpx (async), Pydantic, pandas, pytz
- **Frontend:** React 19+, TypeScript, Vite, TailwindCSS 4+, React Router 7+, Recharts, @tanstack/react-query
- **Comunicacao:** REST API + WebSocket para status em tempo real

## Estrutura do Projeto
```
download-base-transparencia/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, rotas, startup
│   │   ├── config.py            # Modelo Pydantic de configuracao
│   │   ├── models/              # schemas.py, checkpoint.py
│   │   ├── routers/             # config_router, download_router, logs_router, progress_router
│   │   ├── services/            # downloader, token_manager, csv_writer, checkpoint_service, log_service
│   │   ├── core/                # rate_limiter, websocket
│   │   └── utils/               # timezone
│   ├── data/                    # CSVs gerados
│   ├── logs/                    # Logs de execucao
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/                 # client.ts, endpoints.ts
│   │   ├── hooks/               # useConfig, useDownload, useWebSocket, useLogs
│   │   ├── pages/               # 10 paginas (ConfigTokens, Execucao, Progresso, etc.)
│   │   ├── components/          # layout/ (Sidebar, MainLayout) + ui/ (Badge, Gauge, TokenCard, ProgressGrid)
│   │   ├── styles/              # index.css (Tailwind)
│   │   └── types/               # index.ts
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
├── scripts/                     # setup.sh, dev.sh, start.sh
├── Makefile
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
└── ARQUITETURA.md               # Documento completo de arquitetura
```

## Convencoes de Codigo
- **Python:** snake_case (arquivos, funcoes, variaveis), PascalCase (classes)
- **TypeScript:** PascalCase (componentes), camelCase (funcoes/vars), prefix `use` (hooks)
- **Rotas API:** kebab-case (ex: `/api/config/rate-limit`)
- **Variaveis de ambiente:** UPPER_SNAKE_CASE
- **Commits:** Conventional Commits — `feat(backend): descricao`, `fix(frontend): descricao`

## Imports
**Python:** stdlib → terceiros → locais (separados por linha em branco)
**TypeScript:** react → libs externas → componentes → hooks → types

## Arquitetura Backend
- Camadas: `routers/` → `services/` → `core/`
- Persistencia: JSON (config, checkpoints) + CSV (dados) + TXT (logs)
- Motor async: httpx com controle centralizado de rate limit
- WebSocket: `/ws/status` para streaming de metricas em tempo real

## Arquitetura Frontend
- SPA com React Router (10 rotas)
- Sidebar fixa (240px) + area de conteudo
- @tanstack/react-query para cache e estado de servidor
- WebSocket hook com reconexao automatica
- Design system: Inter (corpo) + JetBrains Mono (dados)
- Light/Dark mode com cores semanticas

## Regras de Negocio Criticas
- Cada token tem contador independente por janela de 60s
- Madrugada (00h-06h Brasilia): ate 590 req/min | Dia (06h-24h): ate 390 req/min
- HTTP 429 → troca token | HTTP 401 → remove token | HTTP 5xx → retry 3x backoff
- Checkpoint salvo apos cada pagina com sucesso
- Lista vazia = fim da paginacao do periodo

## Comandos
```bash
make setup    # Setup inicial (venv + npm ci)
make dev      # Desenvolvimento (backend + frontend com hot reload)
make start    # Producao local (build frontend + uvicorn)
make test     # Rodar testes backend
make lint     # Lint backend + frontend
```

## Referencia
Consultar `ARQUITETURA.md` para especificacoes completas de requisitos, validacoes, design, interfaces e DevOps.
