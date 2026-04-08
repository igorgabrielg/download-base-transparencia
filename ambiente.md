# Download Base Transparência — Configuração Técnica do Ambiente

---

## 1. Stack Tecnológica

### Backend

| Tecnologia | Versão | Justificativa |
|---|---|---|
| Python | 3.12+ | Suporte nativo a `asyncio`, `zoneinfo`, performance melhorada |
| FastAPI | 0.115+ | Async nativo, WebSocket, validação automática via Pydantic |
| Uvicorn | 0.32+ | Servidor ASGI de alta performance |
| httpx | 0.28+ | Cliente HTTP async (substitui `requests` + `aiohttp`) |
| Pydantic | 2.10+ | Validação e serialização de configurações |
| pandas | 2.2+ | Manipulação e escrita de CSV |
| pytz | 2024.2+ | Compatibilidade com fusos horários |

### Frontend

| Tecnologia | Versão | Justificativa |
|---|---|---|
| React | 19+ | Componentização, ecossistema maduro para dashboards |
| TypeScript | 5.6+ | Tipagem estática, segurança em tempo de desenvolvimento |
| Vite | 6+ | Build rápido, HMR, proxy integrado |
| TailwindCSS | 4+ | Estilização utilitária alinhada ao design system definido |
| React Router | 7+ | Roteamento SPA para as 10 telas |
| Recharts | 2.15+ | Gráficos/gauges para monitoramento |
| Lucide React | 0.470+ | Ícones consistentes e leves |
| Axios | 1.7+ | Cliente HTTP com interceptors |

### Bibliotecas Complementares

**Backend:** `uuid` (stdlib), `logging` (stdlib), `pathlib` (stdlib), `python-dotenv`

**Frontend:** `clsx`, `tailwind-merge`, `react-hot-toast`, `@tanstack/react-query`

---

## 2. Estrutura de Pastas

```
download-base-transparencia/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, rotas, startup
│   │   ├── config.py                # Modelo Pydantic de configuração
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py           # Schemas Pydantic (request/response)
│   │   │   └── checkpoint.py        # Modelo de checkpoint
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── config_router.py     # CRUD de configurações
│   │   │   ├── download_router.py   # Controle de execução
│   │   │   ├── logs_router.py       # Consulta de logs
│   │   │   └── progress_router.py   # Progresso e checkpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── downloader.py        # Motor de download async
│   │   │   ├── token_manager.py     # Rotação e rate limit de tokens
│   │   │   ├── csv_writer.py        # Escrita incremental CSV
│   │   │   ├── checkpoint_service.py # Persistência de checkpoints
│   │   │   └── log_service.py       # Leitura/filtro de logs
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── rate_limiter.py      # Controle de janela 60s por token
│   │   │   └── websocket.py         # WebSocket para streaming de status
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── timezone.py          # Helper de fuso horário
│   ├── data/                        # Diretório padrão de saída (CSVs)
│   ├── logs/                        # Diretório padrão de logs
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.tsx                 # Entry point
│   │   ├── App.tsx                  # Router principal
│   │   ├── api/
│   │   │   ├── client.ts            # Axios instance configurada
│   │   │   └── endpoints.ts         # Funções de chamada à API
│   │   ├── hooks/
│   │   │   ├── useConfig.ts         # Hook de configuração
│   │   │   ├── useDownload.ts       # Hook de controle de download
│   │   │   ├── useWebSocket.ts      # Hook de WebSocket
│   │   │   └── useLogs.ts           # Hook de logs
│   │   ├── pages/
│   │   │   ├── ConfigTokens.tsx
│   │   │   ├── ConfigPeriodo.tsx
│   │   │   ├── ConfigRateLimit.tsx
│   │   │   ├── ConfigEndpoints.tsx
│   │   │   ├── ConfigSaida.tsx
│   │   │   ├── Execucao.tsx
│   │   │   ├── MonitorTokens.tsx
│   │   │   ├── Logs.tsx
│   │   │   ├── Progresso.tsx
│   │   │   └── Retomada.tsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── MainLayout.tsx
│   │   │   └── ui/
│   │   │       ├── Badge.tsx
│   │   │       ├── Gauge.tsx
│   │   │       ├── TokenCard.tsx
│   │   │       └── ProgressGrid.tsx
│   │   ├── styles/
│   │   │   └── index.css            # Tailwind directives + tokens CSS
│   │   └── types/
│   │       └── index.ts             # Tipos compartilhados
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── package.json
└── README.md
```

---

## 3. Configuração do Ambiente

### 3.1 Backend — `requirements.txt`

```
fastapi==0.115.12
uvicorn[standard]==0.34.2
httpx==0.28.1
pydantic==2.11.1
pydantic-settings==2.8.1
pandas==2.2.3
pytz==2024.2
python-dotenv==1.1.0
websockets==15.0.1
```

### 3.2 Frontend — `package.json`

```json
{
  "name": "download-base-transparencia-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.5.0",
    "axios": "^1.7.9",
    "@tanstack/react-query": "^5.67.0",
    "recharts": "^2.15.0",
    "lucide-react": "^0.470.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.0.0",
    "react-hot-toast": "^2.5.2"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.6.0",
    "vite": "^6.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0"
  }
}
```

### 3.3 `vite.config.ts`

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
```

### 3.4 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"]
}
```

### 3.5 Variáveis de Ambiente — `.env`

```env
# === Backend ===
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

# Tokens do Portal da Transparência
TOKEN_1=
TOKEN_2=
TOKEN_3=

# API do Portal da Transparência
API_BASE_URL=https://api.portaldatransparencia.gov.br/api-de-dados

# Rate Limits (req/min)
MAX_REQ_MADRUGADA=590
MAX_REQ_DIA=390
MAX_REQ_RESTRITA=170

# Período padrão
ANO_INICIO=2014
ANO_FIM=2026

# Diretórios
DIRETORIO_SAIDA=./data
DIRETORIO_LOGS=./logs

# Fuso horário
FUSO_HORARIO=America/Sao_Paulo

# === Frontend ===
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 4. Padrões de Código

### Convenções de Nomenclatura

| Contexto | Padrão | Exemplo |
|---|---|---|
| Arquivos Python | snake_case | `token_manager.py` |
| Classes Python | PascalCase | `TokenManager` |
| Funções/variáveis Python | snake_case | `get_active_token()` |
| Componentes React | PascalCase | `TokenCard.tsx` |
| Hooks React | camelCase com `use` | `useDownload.ts` |
| Variáveis/funções TS | camelCase | `handleStart()` |
| Rotas API | kebab-case | `/api/config/rate-limit` |
| Variáveis de ambiente | UPPER_SNAKE_CASE | `API_BASE_URL` |

### Estrutura de Arquivos

- **Backend:** organizado por camada (`routers` → `services` → `core`)
- **Frontend:** organizado por feature nas `pages/`, componentes reutilizáveis em `components/ui/`
- Um componente por arquivo, exportação nomeada

### Padrões de Importação

**Python:** stdlib → terceiros → locais, separados por linha em branco

```python
import asyncio
from pathlib import Path

from fastapi import APIRouter
import httpx

from app.services.token_manager import TokenManager
```

**TypeScript:** react → libs → componentes → hooks → types

```ts
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/Badge";
import { useConfig } from "@/hooks/useConfig";
import type { Config } from "@/types";
```

---

## 5. Integração Frontend-Backend

### Proxy

Configurado no `vite.config.ts` (seção 3.3): `/api` → `localhost:8000`, `/ws` → WebSocket.

### Cliente HTTP Base — `api/client.ts`

```ts
import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});
```

### Endpoints — `api/endpoints.ts`

```ts
import { api } from "./client";

export const configApi = {
  get: () => api.get("/config"),
  save: (data: ConfigPayload) => api.put("/config", data),
  validateTokens: () => api.post("/config/tokens/validate"),
};

export const downloadApi = {
  start: () => api.post("/download/start"),
  pause: () => api.post("/download/pause"),
  resume: () => api.post("/download/resume"),
  stop: () => api.post("/download/stop"),
};

export const logsApi = {
  list: (params: LogFilters) => api.get("/logs", { params }),
};

export const progressApi = {
  get: (params?: ProgressFilters) => api.get("/progress", { params }),
  checkpoints: () => api.get("/progress/checkpoints"),
};
```

### Hooks de API

Utilizam `@tanstack/react-query` para cache, refetch e estado de loading:

```ts
// hooks/useConfig.ts
export function useConfig() {
  return useQuery({ queryKey: ["config"], queryFn: configApi.get });
}
```

### WebSocket (status em tempo real)

- Endpoint backend: `ws://localhost:8000/ws/status`
- Envia JSON com: `status_execucao`, `token_ativo`, `req_minuto`, `endpoint_atual`, `ano_mes_atual`, `pagina_atual`, `total_registros`, `token_statuses[]`
- Hook `useWebSocket` reconecta automaticamente e expõe estado reativo

---

## 6. Nível de Autoridade da IA — `controlled`

Diretrizes para o projeto gerado:

- **Execução mediante aprovação:** a IA deve apresentar o plano de ação antes de executar qualquer modificação de código e aguardar confirmação do usuário
- **Criação de arquivos:** permitida apenas após confirmação explícita
- **Comandos destrutivos:** proibidos sem aprovação (delete, overwrite, force push)
- **Instalação de dependências:** apresentar lista e aguardar aprovação antes de executar `pip install` ou `npm install`
- **Decisões de arquitetura:** propor alternativas e justificativas, mas a decisão final é do usuário
- **Refatorações:** somente quando solicitadas; não refatorar proativamente
- **Testes:** pode executar testes automaticamente, mas não deve alterar testes existentes sem aprovação
- **Git:** pode fazer commits locais, mas push/merge requer aprovação explícita

---

*Documento gerado pelo Agente AMBIENTE — Sistema Arquiteto de Software*