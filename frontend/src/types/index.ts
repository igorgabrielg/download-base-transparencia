// --- Enums ---

export type EndpointType = "despesas" | "receitas";

export type CheckpointStatus = "pendente" | "em_andamento" | "concluido" | "erro" | "arquivo_ausente";

export type TokenStatusEnum = "ativo" | "em_espera" | "invalido" | "limite_atingido";

export type LogLevel = "info" | "warning" | "error";

export type ExecutionStatus = "parado" | "executando" | "pausado" | "erro" | "concluido";

export type FormatoNomeArquivo = "por_ano_mes" | "por_ano";

export type ModoEscrita = "append" | "overwrite";

export type TokenId = "token_1" | "token_2" | "token_3";

export type TokenValidationStatus = "valido" | "invalido" | "nao_testado";

// --- 4.1 Config (config.json) ---

export interface Config {
  id: string;
  tokens_count: number;
  token_1: string;
  token_2: string;
  token_3: string;
  token_1_set: boolean;
  token_2_set: boolean;
  token_3_set: boolean;
  ano_inicio: number;
  ano_fim: number;
  mes_inicio: number;
  mes_fim: number;
  max_req_madrugada: number;
  max_req_dia: number;
  max_req_restrita: number;
  velocidade_req_min: number;
  fuso_horario: string;
  tamanho_pagina: number;
  baixar_despesas: boolean;
  baixar_receitas: boolean;
  base_url: string;
  diretorio_saida: string;
  formato_nome_arquivo: FormatoNomeArquivo;
  modo_escrita: ModoEscrita;
  diretorio_logs: string;
  gemini_api_key: string;
  anthropic_api_key: string;
  ia_provider: "gemini" | "claude";
  ia_model: string;
  active: boolean;
  created_at: string;
  last_update: string;
}

// --- Config Request/Response ---

export interface ConfigTokensRequest {
  token_1: string;
  token_2: string;
  token_3: string;
  validar_tokens: boolean;
}

export interface TokenValidationResult {
  token_id: TokenId;
  status: TokenValidationStatus;
  message: string;
}

export interface ConfigTokensResponse {
  token_1: string;
  token_2: string;
  token_3: string;
  validations: TokenValidationResult[];
}

export interface ConfigPeriodoRequest {
  ano_inicio: number;
  ano_fim: number;
  mes_inicio: number;
  mes_fim: number;
}

export interface ConfigPeriodoResponse {
  ano_inicio: number;
  ano_fim: number;
  mes_inicio: number;
  mes_fim: number;
  total_meses: number;
}

export interface ConfigRateLimitRequest {
  max_req_madrugada: number;
  max_req_dia: number;
  max_req_restrita: number;
  velocidade_req_min: number;
  fuso_horario: string;
  tamanho_pagina: number;
}

export interface ConfigRateLimitResponse {
  max_req_madrugada: number;
  max_req_dia: number;
  max_req_restrita: number;
  velocidade_req_min: number;
  fuso_horario: string;
  tamanho_pagina: number;
}

export interface ConfigEndpointsRequest {
  baixar_despesas: boolean;
  baixar_receitas: boolean;
  base_url: string;
}

export interface ConfigEndpointsResponse {
  baixar_despesas: boolean;
  baixar_receitas: boolean;
  base_url: string;
}

export interface ConfigSaidaRequest {
  diretorio_saida: string;
  formato_nome_arquivo: FormatoNomeArquivo;
  modo_escrita: ModoEscrita;
  diretorio_logs: string;
}

export interface ConfigSaidaResponse {
  diretorio_saida: string;
  formato_nome_arquivo: FormatoNomeArquivo;
  modo_escrita: ModoEscrita;
  diretorio_logs: string;
}

// --- 4.2 Checkpoint ---

export interface Checkpoint {
  id: string;
  endpoint: EndpointType;
  ano: number;
  mes: number;
  pagina: number;
  total_registros: number;
  status: CheckpointStatus;
  arquivo_csv: string;
  active: boolean;
  created_at: string;
  last_update: string;
}

export interface CheckpointListResponse {
  items: Checkpoint[];
}

// --- 4.3 LogEntry ---

export interface LogEntry {
  id: string;
  timestamp: string;
  nivel: LogLevel;
  token_id: TokenId | null;
  endpoint: EndpointType | null;
  ano: number | null;
  mes: number | null;
  pagina: number | null;
  status_http: number | null;
  mensagem: string;
  registros_obtidos: number | null;
}

export interface LogFilters {
  filtro_data_inicio?: string;
  filtro_data_fim?: string;
  filtro_nivel_log?: LogLevel;
  filtro_endpoint?: EndpointType;
  filtro_token?: TokenId;
  busca_texto?: string;
  limit?: number;
  offset?: number;
}

export interface LogListResponse {
  items: LogEntry[];
  total: number;
}

// --- 4.4 TokenStatus (runtime) ---

export interface TokenStatus {
  id: string;
  token_id: TokenId;
  status: TokenStatusEnum;
  req_minuto_atual: number;
  limite_aplicavel: number;
  janela_inicio: string | null;
  tempo_para_reset: number;
  active: boolean;
  created_at: string;
  last_update: string;
}

// --- 4.5 DownloadProgress ---

export interface DownloadProgress {
  id: string;
  endpoint: EndpointType;
  ano: number;
  mes: number;
  status: CheckpointStatus;
  arquivo_csv: string;
  tamanho_arquivo: number;
  total_registros: number;
  ultima_pagina: number;
  active: boolean;
  created_at: string;
  last_update: string;
}

export interface ProgressFilters {
  filtro_ano?: number;
  filtro_endpoint?: EndpointType;
  exibir_apenas_pendentes?: boolean;
}

export interface ProgressListResponse {
  items: DownloadProgress[];
  total_arquivos_gerados: number;
  tamanho_total_disco: number;
  percentual_concluido: number;
}

// --- Execution (Painel de Execucao) ---

export interface DownloadStatus {
  status: ExecutionStatus;
  token_ativo: TokenId | null;
  req_minuto: number;
  endpoint_atual: EndpointType | null;
  ano_mes_atual: string | null;
  pagina_atual: number;
  total_registros: number;
  token_statuses: TokenStatus[];
  mensagem: string;
  msg_seq: number;
}

// --- Retomada de Download ---

export interface ResumeDownloadRequest {
  endpoint_retomada: EndpointType;
  ano_retomada: number;
  mes_retomada: number;
  pagina_retomada: number;
  ignorar_arquivos_existentes: boolean;
}

export interface ConfigIARequest {
  gemini_api_key: string;
  anthropic_api_key: string;
  ia_provider: "gemini" | "claude";
  ia_model: string;
}

export interface ConfigIAResponse {
  gemini_api_key: string;
  anthropic_api_key: string;
  ia_provider: "gemini" | "claude";
  ia_model: string;
}


// --- Chat RAG ---

export interface ChatRequest {
  pergunta: string;
}

export interface ChatResponse {
  resposta: string;
  contexto: string[];
}


