# Download Base Transparencia

Sistema para download massivo de dados do Portal da Transparencia do Governo Federal. Gerencia multiplos tokens com rotacao inteligente, rate limit adaptativo por horario e salvamento incremental em CSV + SQLite.

## Requisitos

- Python 3.12+
- Node.js 18+
- npm 9+

## Configuracao

### 1. Backend

```bash
cd backend
cp .env.example .env
cp data/config.example.json data/config.json
```

Edite o arquivo `backend/.env` e preencha pelo menos o `TOKEN_1`:

```env
TOKEN_1=seu_token_aqui
```

Para obter um token, cadastre-se em: https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email

### 2. Frontend

```bash
cd frontend
cp .env.example .env
```

Em desenvolvimento, deixe as variaveis vazias. O proxy do Vite redireciona as chamadas para o backend automaticamente.

### 3. Instalar dependencias

```bash
make setup
```

Ou manualmente:

```bash
# Backend
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm ci
```

## Executando

### Desenvolvimento

```bash
make dev
```

Isso inicia o backend (uvicorn com hot reload na porta 8000) e o frontend (Vite na porta 5173).

### Producao local

```bash
make start
```

## Configuracao via Interface

Apos iniciar o sistema, acesse `http://localhost:5173` e configure:

| Pagina | Descricao |
|--------|-----------|
| **Tokens** | Cadastre 1 a 3 tokens da API. Com multiplos tokens, o sistema rotaciona automaticamente ao atingir o limite |
| **Periodo** | Defina o intervalo de meses/anos para download |
| **Rate Limit** | Ajuste limites por faixa horaria (dia/noite) e velocidade de requisicao |
| **Endpoints** | Selecione quais dados baixar (Despesas, Receitas) |
| **Saida** | Escolha a pasta onde os CSVs serao salvos |

## Variaveis de Ambiente

### Backend (`backend/.env`)

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `TOKEN_1` | Token principal da API (obrigatorio) | - |
| `TOKEN_2` | Token secundario (opcional, para rotacao) | - |
| `TOKEN_3` | Token terciario (opcional) | - |
| `APP_PORT` | Porta do servidor | `8000` |
| `MAX_REQ_DIA` | Limite req/min (06h-24h) | `390` |
| `MAX_REQ_MADRUGADA` | Limite req/min (00h-06h) | `590` |
| `DIRETORIO_SAIDA` | Pasta para CSVs | `./data` |
| `DIRETORIO_LOGS` | Pasta para logs | `./logs` |
| `FRONTEND_URL` | URL do frontend (CORS) | `http://localhost:5173` |

### Frontend (`frontend/.env`)

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `VITE_API_URL` | URL da API (vazio em dev) | - |
| `VITE_WS_URL` | URL do WebSocket (vazio em dev) | - |

### Config runtime (`backend/data/config.json`)

Este arquivo e criado automaticamente pela interface. Voce pode copiar o exemplo para comecar:

```bash
cp backend/data/config.example.json backend/data/config.json
```

Edite o `token_1` com seu token. As demais configuracoes podem ser alteradas pela interface web.

## Dados gerados

### CSVs
Salvos na pasta de saida configurada, nomeados por periodo: `despesas_2024_01.csv`

### SQLite
O arquivo `backend/data/transparencia.db` e gerado automaticamente e contem todos os dados baixados. Pode ser consultado por qualquer pessoa com um cliente SQL:

```bash
sqlite3 backend/data/transparencia.db "SELECT * FROM despesas WHERE _ano=2024 AND _mes=1;"
```

### Progresso
O grid de progresso na interface mostra:
- **Verde**: periodo baixado, arquivo presente
- **Azul**: parcialmente baixado (ultima pagina registrada)
- **Amarelo**: baixado (banco sabe) mas CSV ausente na pasta
- **Vermelho**: nao baixado

## Rotacao de Tokens

Com multiplos tokens configurados, o sistema:
1. Usa o token atual ate atingir o limite de req/min
2. Rotaciona automaticamente para o proximo token disponivel
3. Se todos os tokens atingirem o limite, aguarda o reset da janela (60s)
4. Com apenas 1 token, pausa e informa que o limite foi atingido

## Stack

- **Backend:** Python 3.12, FastAPI, httpx, Pydantic, pandas
- **Frontend:** React 19, TypeScript, Vite, TailwindCSS 4, React Router, Recharts, @tanstack/react-query
- **Comunicacao:** REST API + WebSocket para status em tempo real
