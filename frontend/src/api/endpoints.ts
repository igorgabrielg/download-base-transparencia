import { api } from "./client";
import type {
  Config,
  ConfigTokensRequest,
  ConfigTokensResponse,
  ConfigPeriodoRequest,
  ConfigPeriodoResponse,
  ConfigRateLimitRequest,
  ConfigRateLimitResponse,
  ConfigEndpointsRequest,
  ConfigEndpointsResponse,
  ConfigSaidaRequest,
  ConfigSaidaResponse,
  TokenValidationResult,
  DownloadStatus,
  LogFilters,
  LogListResponse,
  ProgressListResponse,
  CheckpointListResponse,
  ResumeDownloadRequest,
  ConfigIARequest,
  ConfigIAResponse,
  ChatResponse,
} from "@/types";


export const configApi = {
  get: () => api.get<Config>("/config").then((r) => r.data),
  updateTokens: (data: ConfigTokensRequest) =>
    api.put<ConfigTokensResponse>("/config/tokens", data).then((r) => r.data),
  validateTokens: () =>
    api.post<TokenValidationResult[]>("/config/tokens/validate").then((r) => r.data),
  updatePeriodo: (data: ConfigPeriodoRequest) =>
    api.put<ConfigPeriodoResponse>("/config/periodo", data).then((r) => r.data),
  updateRateLimit: (data: ConfigRateLimitRequest) =>
    api.put<ConfigRateLimitResponse>("/config/rate-limit", data).then((r) => r.data),
  updateEndpoints: (data: ConfigEndpointsRequest) =>
    api.put<ConfigEndpointsResponse>("/config/endpoints", data).then((r) => r.data),
  updateSaida: (data: ConfigSaidaRequest) =>
    api.put<ConfigSaidaResponse>("/config/saida", data).then((r) => r.data),
  updateIA: (data: ConfigIARequest) =>
    api.put<ConfigIAResponse>("/config/ia", data).then((r) => r.data),
  pickDirectory: () =>
    api.post<{ path: string; error: string | null }>("/config/pick-directory", null, { timeout: 120000 }).then((r) => r.data),
};

export const downloadApi = {
  start: () => api.post<DownloadStatus>("/download/start").then((r) => r.data),
  pause: () => api.post<DownloadStatus>("/download/pause").then((r) => r.data),
  resume: () => api.post<DownloadStatus>("/download/resume").then((r) => r.data),
  stop: () => api.post<DownloadStatus>("/download/stop").then((r) => r.data),
  resumeFromCheckpoint: (data: ResumeDownloadRequest) =>
    api.post<DownloadStatus>("/download/resume-from-checkpoint", data).then((r) => r.data),
};

export const logsApi = {
  list: (params?: LogFilters) =>
    api.get<LogListResponse>("/logs", { params }).then((r) => r.data),
};

export const progressApi = {
  get: (params?: { filtro_endpoint?: string; filtro_ano?: number; exibir_apenas_pendentes?: boolean }) =>
    api.get<ProgressListResponse>("/progress", { params }).then((r) => r.data),
  checkpoints: () =>
    api.get<CheckpointListResponse>("/progress/checkpoints").then((r) => r.data),
};

export const iaApi = {
  analyze: () => api.post<{ message: string }>("/ia/analyze").then((r) => r.data),
  synthesize: () => api.post<{ message: string }>("/ia/synthesize").then((r) => r.data),
  index: () => api.post<{ message: string }>("/ia/index").then((r) => r.data),
  chat: (pergunta: string) => api.post<ChatResponse>("/ia/chat", { pergunta }, { timeout: 60000 }).then((r) => r.data),
  runPipelineCompleto: () => api.post<{ message: string }>("/ia/pipeline-completo").then((r) => r.data),
};
