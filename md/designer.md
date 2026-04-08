# Download Base Transparência — Diretrizes de Design

---

## 1. Identidade Visual

### Paleta de Cores (Light Mode)

| Papel | Cor | Hex |
|-------|-----|-----|
| Primária | Cinza escuro | `#1a1a1a` |
| Secundária | Cinza claro | `#d4d4d4` |
| Destaque | Azul | `#3b82f6` |
| Fundo | Branco | `#ffffff` |
| Texto | Cinza escuro | `#1a1a1a` |
| Fundo secundário | Cinza off-white | `#f5f5f5` |
| Borda | Cinza médio | `#e5e5e5` |

### Cores Semânticas

| Estado | Hex | Uso |
|--------|-----|-----|
| Success | `#22c55e` | Token válido, download concluído |
| Warning | `#eab308` | Token em espera, pausado |
| Error | `#ef4444` | Token inválido, falha, erro HTTP |
| Info | `#3b82f6` | Em andamento, notificações |
| Orange | `#f97316` | Limite atingido (token) |

### Variantes de Estado

| Estado | Tratamento |
|--------|-----------|
| Hover | Destaque `#2563eb`; backgrounds ganham 5% de opacidade da primária |
| Active | Destaque `#1d4ed8` |
| Disabled | Opacidade 40%, cursor `not-allowed` |
| Focus | Ring `#3b82f6` 2px offset 2px |

### Gradientes

- Header/Hero: `linear-gradient(135deg, #1a1a1a 0%, #374151 100%)`
- Cards destaque: `linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%)`

---

## 2. Tipografia

**Família:** `Inter` (corpo) / `JetBrains Mono` (dados, logs, tokens)

| Elemento | Tamanho | Peso | Line-height |
|----------|---------|------|-------------|
| h1 | 28px | 700 | 1.2 |
| h2 | 22px | 600 | 1.3 |
| h3 | 18px | 600 | 1.3 |
| h4 | 16px | 600 | 1.4 |
| h5 | 14px | 600 | 1.4 |
| h6 | 12px | 600 | 1.5 |
| Body | 14px | 400 | 1.5 |
| Caption | 12px | 400 | 1.4 |
| Mono/Dados | 13px | 400 | 1.5 |

---

## 3. Tom de Voz / Microcopy

**Diretriz:** Profissional, direto, técnico sem ser intimidador. Frases curtas e orientadas a ação.

### Padrões

| Contexto | Exemplo |
|----------|---------|
| Botão primário | "Iniciar Download", "Salvar Configuração" |
| Botão secundário | "Cancelar", "Restaurar Padrões" |
| Botão destrutivo | "Parar Download" |
| Sucesso | "Configuração salva com sucesso." |
| Erro validação | "Informe pelo menos um token válido." |
| Erro conexão | "Não foi possível conectar à API. Verifique a URL e tente novamente." |
| Erro rate limit | "Token 1 atingiu o limite. Alternando para Token 2." |
| Placeholder input | "Cole o token aqui" / "Ex: /home/user/dados" |
| Campo vazio | "Nenhum log encontrado para os filtros aplicados." |
| Confirmação | "Deseja parar o download em andamento? O progresso será salvo." |
| Tooltip | "Requisições permitidas por minuto entre 00h e 06h (horário de Brasília)." |

---

## 4. Componentes de UI

### Espacamento Base

- Unidade: `4px`. Escala: 4, 8, 12, 16, 24, 32, 48, 64.
- Padding de cards: `24px`
- Gap entre cards: `16px`
- Margem lateral do container: `24px` (mobile `16px`)
- Border-radius: `8px` (cards/modais), `6px` (inputs/botões), `4px` (badges)

### Layout Geral

- Container max-width: `1200px`, centrado
- Sidebar fixa à esquerda (`240px`) com navegação entre telas
- Área de conteúdo à direita, flex column
- Breakpoints: `640px` (mobile), `768px` (tablet), `1024px` (desktop)

### Por Tela

**5.1–5.5 Telas de Configuração** (`/config/*`)
- Layout: single column, max-width `640px`
- Componentes: form com inputs empilhados, labels acima, botões alinhados à direita
- Agrupamento em sections com `h3` como separador
- Inputs com borda `#e5e5e5`, foco `#3b82f6`

**5.6 Painel de Execução** (`/execucao`)
- Layout: grid 2 colunas (desktop), stack (mobile)
- Coluna esquerda: métricas em cards (status badge, token ativo, req/min gauge, endpoint/ano/mês/página)
- Coluna direita: console de logs em tempo real (fundo `#1a1a1a`, texto mono verde/branco)
- Barra de ações (Iniciar/Pausar/Retomar/Parar) fixada no topo da área de conteúdo
- Gauge de req/min: barra horizontal preenchida com cor semântica (verde < 70%, amarelo 70–90%, vermelho > 90%)

**5.7 Monitor de Tokens** (`/monitor/tokens`)
- Layout: grid 3 colunas (1 card por token), stack em mobile
- Card: badge de status (cor semântica), barra de progresso, countdown timer
- Indicador de faixa horária ativa no topo da página

**5.8 Visualizador de Logs** (`/logs`)
- Layout: barra de filtros horizontal (flex wrap) + tabela abaixo
- Tabela: linhas zebradas (`#f5f5f5` / `#ffffff`), hover `#eff6ff`
- Badges coloridos para nível de log (info=azul, warning=amarelo, error=vermelho)
- Paginação na base da tabela

**5.9 Progresso de Downloads** (`/progresso`)
- Layout: filtros no topo + grid calendário abaixo
- Grid: 12 colunas (meses) × N linhas (anos), células `48×48px` com cor semântica
- Legenda de cores abaixo do grid
- Barra de progresso geral no rodapé
- Separação visual despesas/receitas por seções ou tabs

**5.10 Retomada de Download** (`/retomada`)
- Layout: split — form à esquerda, tabela de checkpoints à direita (stack em mobile)
- Botão "Usar" em cada linha da tabela preenche o form automaticamente

### Responsivo

| Breakpoint | Comportamento |
|------------|--------------|
| ≥ 1024px | Sidebar visível, grids multi-coluna |
| 768–1023px | Sidebar colapsável (hamburger), grids 2 colunas |
| < 768px | Sidebar oculta (drawer), tudo single column, tabelas com scroll horizontal |

---

## 5. Dark Mode

### Paleta Dark

| Papel | Hex |
|-------|-----|
| Fundo base | `#0a0a0a` |
| Superfície nível 1 | `#171717` |
| Superfície nível 2 | `#262626` |
| Superfície nível 3 | `#404040` |
| Borda | `#404040` |
| Texto primário | `#fafafa` |
| Texto secundário | `#a3a3a3` |
| Destaque | `#60a5fa` (azul mais claro para contraste) |

### Cores Semânticas (Dark)

| Estado | Hex |
|--------|-----|
| Success | `#4ade80` |
| Warning | `#facc15` |
| Error | `#f87171` |
| Info | `#60a5fa` |
| Orange | `#fb923c` |

### Regras de Adaptação

- Elevação representada por luminosidade crescente (não sombra)
- Inputs: fundo `#262626`, borda `#404040`, foco `#60a5fa`
- Tabelas: zebra `#171717` / `#0a0a0a`, hover `#1e3a5f`
- Console de logs mantém fundo `#0a0a0a` (já escuro)
- Badges mantêm cores semânticas com fundo em opacidade 15% + texto na cor semântica
- Gradiente header: `linear-gradient(135deg, #0a0a0a 0%, #1f2937 100%)`
- Transição light↔dark: `transition: background-color 200ms, color 200ms`

---

*Documento gerado pelo Agente DESIGNER — Sistema Arquiteto de Software*