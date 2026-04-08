# Download Base Transparência — Configuração de DevOps

---

## 1. Repositório Git

### Plataforma
**GitHub** — repositório privado `download-base-transparencia`

### Estrutura de Branches

| Branch | Finalidade | Proteção |
|--------|-----------|----------|
| `main` | Código estável, releases | Branch protegida, merge apenas via PR |
| `develop` | Integração de features | Branch padrão de desenvolvimento |
| `feature/*` | Novas funcionalidades | Ex: `feature/token-rotation`, `feature/log-viewer` |
| `fix/*` | Correções de bugs | Ex: `fix/rate-limit-reset` |
| `release/*` | Preparação de release | Ex: `release/1.0.0` |

**Fluxo:** `feature/*` → PR → `develop` → PR → `main` (com tag de versão)

### Convenção de Commits

Padrão **Conventional Commits**:

```
<tipo>(<escopo>): <descrição curta>

Tipos: feat, fix, docs, style, refactor, test, chore, ci
Escopo: backend, frontend, config, download, tokens, logs
```

Exemplos:
- `feat(backend): implementar rotação automática de tokens`
- `fix(frontend): corrigir gauge de req/min no painel de execução`
- `chore(config): atualizar dependências do requirements.txt`

### .gitignore

```gitignore
# === Python ===
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
env/

# === Node ===
node_modules/
frontend/dist/

# === Dados e Logs (gerados em runtime) ===
backend/data/*.csv
backend/logs/*.txt
backend/logs/*.log

# === Configuração sensível ===
.env
.env.local
.env.production
backend/.env

# === Checkpoints (estado local) ===
backend/checkpoint.json

# === IDE ===
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# === OS ===
Thumbs.db
```

---

## 2. CI/CD Pipeline

> **Nota:** O usuário não selecionou plataforma de CI/CD. A configuração abaixo usa **GitHub Actions** (integrado ao GitHub, gratuito para repositórios privados com 2.000 min/mês) como recomendação natural.

### Stages

`lint` → `test` → `build` → `deploy` (deploy manual/placeholder por não haver plataforma de deploy)

### Configuração — `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt ruff
      - run: ruff check app/
      - run: ruff format --check app/

  lint-frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npx tsc --noEmit

  test-backend:
    needs: lint-backend
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt pytest pytest-asyncio
      - run: pytest tests/ -v

  build-frontend:
    needs: lint-frontend
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist
          retention-days: 7
```

### Pre-commit Hooks

Arquivo `.pre-commit-config.yaml` na raiz:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: no-commit-to-branch
        args: [--branch, main]
```

Setup:
```bash
pip install pre-commit
pre-commit install
```

---

## 3. Deploy

> **Nota:** O usuário não selecionou plataforma de deploy. O projeto é projetado para execução local (máquina do pesquisador). Abaixo estão scripts de setup e execução local como alternativa de "deploy".

### Ambientes

| Ambiente | Finalidade | Configuração |
|----------|-----------|--------------|
| `development` | Desenvolvimento local | Hot reload, logs verbose, proxy Vite |
| `production` | Execução final pelo usuário | Build otimizado, uvicorn em modo produção |

### Variáveis de Ambiente por Ambiente

**development** (`.env`):
```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=DEBUG
```

**production** (`.env.production`):
```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

### Scripts de Setup e Execução

**`scripts/setup.sh`** — Setup inicial:
```bash
#!/usr/bin/env bash
set -e

echo "=== Backend ==="
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data logs
cp .env.example .env 2>/dev/null || true

echo "=== Frontend ==="
cd ../frontend
npm ci
echo "Setup concluído. Configure os tokens em backend/.env"
```

**`scripts/dev.sh`** — Desenvolvimento:
```bash
#!/usr/bin/env bash
set -e
trap 'kill 0' EXIT

cd backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

cd ../frontend
npm run dev &

wait
```

**`scripts/start.sh`** — Execução em produção local:
```bash
#!/usr/bin/env bash
set -e

# Build frontend
cd frontend && npm run build
cp -r dist/ ../backend/static/

# Start backend servindo frontend estático
cd ../backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### Makefile (atalhos)

```makefile
.PHONY: setup dev start test lint

setup:
	bash scripts/setup.sh

dev:
	bash scripts/dev.sh

start:
	bash scripts/start.sh

test:
	cd backend && source .venv/bin/activate && pytest tests/ -v

lint:
	cd backend && ruff check app/ && ruff format --check app/
	cd frontend && npx tsc --noEmit
```

---

## 4. Monitoramento

### Logs e Observabilidade

O sistema já possui logging nativo em `logs.txt`. Configuração adicional recomendada:

**Backend — `logging` config em `main.py`:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)
```

**Logs estruturados por nível:**

| Nível | Uso |
|-------|-----|
| `INFO` | Requisição realizada, página salva, token rotacionado |
| `WARNING` | HTTP 429, token em espera, retry acionado |
| `ERROR` | HTTP 401/5xx, falha de escrita, token inválido |

### Health Checks

**Endpoint:** `GET /api/health`

```python
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "checks": {
            "config_loaded": Path("config.json").exists(),
            "output_dir_writable": os.access(settings.diretorio_saida, os.W_OK),
            "log_dir_writable": os.access(settings.diretorio_logs, os.W_OK),
        },
    }
```

**Endpoint:** `GET /api/health/api` (testa conectividade com Portal da Transparência)

```python
@app.get("/api/health/api")
async def health_api():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{settings.base_url}/despesas", timeout=5)
            return {"api_reachable": r.status_code != 0, "status_code": r.status_code}
        except httpx.RequestError:
            return {"api_reachable": False}
```

### Alertas Básicos

Como o sistema roda localmente, alertas são implementados via **WebSocket + notificações no frontend**:

| Evento | Nível | Ação no Frontend |
|--------|-------|-----------------|
| Todos os tokens em limite | Warning | Toast amarelo + pausa visual no painel |
| Token marcado inválido (401) | Error | Toast vermelho + badge no Monitor de Tokens |
| 3 retries consecutivos falharam | Error | Toast vermelho + log destacado |
| Download de endpoint concluído | Success | Toast verde + atualização do grid de progresso |
| Disco com < 500MB livre | Warning | Toast amarelo no painel de execução |
| Download completo (todos os períodos) | Success | Notificação de conclusão + status azul |

**Implementação simplificada no backend:**
```python
async def check_disk_space(path: str, min_mb: int = 500) -> bool:
    usage = shutil.disk_usage(path)
    return usage.free > min_mb * 1024 * 1024
```

---

*Documento gerado pelo Agente DEVOPS — Sistema Arquiteto de Software*