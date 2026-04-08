import { z } from "zod";

// --- Enums ---

export const endpointTypeSchema = z.enum(["despesas", "receitas"]);

export const checkpointStatusSchema = z.enum([
  "pendente",
  "em_andamento",
  "concluido",
  "erro",
  "arquivo_ausente",
]);

export const tokenStatusEnumSchema = z.enum([
  "ativo",
  "em_espera",
  "invalido",
  "limite_atingido",
]);

export const logLevelSchema = z.enum(["info", "warning", "error"]);

export const executionStatusSchema = z.enum([
  "parado",
  "executando",
  "pausado",
  "erro",
  "concluido",
]);

export const formatoNomeArquivoSchema = z.enum(["por_ano_mes", "por_ano"]);

export const modoEscritaSchema = z.enum(["append", "overwrite"]);

export const tokenIdSchema = z.enum(["token_1", "token_2", "token_3"]);

export const tokenValidationStatusSchema = z.enum([
  "valido",
  "invalido",
  "nao_testado",
]);

// --- Token alfanumerico ---

const tokenPattern = /^[a-zA-Z0-9]+$/;

// --- 5.1 Configuracao de Tokens (RN01, RN02) ---

export const configTokensRequestSchema = z
  .object({
    token_1: z
      .string()
      .min(1, "Token 1 e obrigatorio")
      .regex(tokenPattern, "Token deve conter apenas caracteres alfanumericos"),
    token_2: z
      .string()
      .regex(tokenPattern, "Token deve conter apenas caracteres alfanumericos")
      .or(z.literal("")),
    token_3: z
      .string()
      .regex(tokenPattern, "Token deve conter apenas caracteres alfanumericos")
      .or(z.literal("")),
    validar_tokens: z.boolean().default(false),
  })
  .superRefine((data, ctx) => {
    // RN02: Token duplicado nao e permitido
    const tokens = [data.token_1, data.token_2, data.token_3].filter(
      (t) => t !== ""
    );
    const unique = new Set(tokens);
    if (unique.size !== tokens.length) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Tokens nao podem ser duplicados",
        path: ["token_2"],
      });
    }

    // RN01: token_2 so valido se token_1 preenchido (implicito pelo min(1))
    // RN02: token_3 nao pode ser igual a token_1 ou token_2
    if (data.token_3 !== "" && data.token_3 === data.token_1) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Token 3 nao pode ser igual ao Token 1",
        path: ["token_3"],
      });
    }
    if (data.token_3 !== "" && data.token_3 === data.token_2) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Token 3 nao pode ser igual ao Token 2",
        path: ["token_3"],
      });
    }
    if (
      data.token_2 !== "" &&
      data.token_2 === data.token_1
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Token 2 nao pode ser igual ao Token 1",
        path: ["token_2"],
      });
    }
  });

// --- 5.2 Configuracao de Periodo (RN04, RN05) ---

export const configPeriodoRequestSchema = z
  .object({
    ano_inicio: z
      .number({ error: "Ano inicio e obrigatorio" })
      .int()
      .min(2004, "Ano minimo: 2004")
      .max(2026, "Ano maximo: 2026"),
    ano_fim: z
      .number({ error: "Ano fim e obrigatorio" })
      .int()
      .min(2004, "Ano minimo: 2004")
      .max(2026, "Ano maximo: 2026"),
    mes_inicio: z.number().int().min(1).max(12).default(1),
    mes_fim: z.number().int().min(1).max(12).default(12),
  })
  .superRefine((data, ctx) => {
    // RN04: ano_fim >= ano_inicio
    if (data.ano_fim < data.ano_inicio) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Ano fim deve ser maior ou igual ao ano inicio",
        path: ["ano_fim"],
      });
    }
    // RN05: Se mesmo ano, mes_fim >= mes_inicio
    if (data.ano_inicio === data.ano_fim && data.mes_fim < data.mes_inicio) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message:
          "Mes fim deve ser maior ou igual ao mes inicio quando no mesmo ano",
        path: ["mes_fim"],
      });
    }
  });

// --- 5.3 Configuracao de Rate Limit ---

export const configRateLimitRequestSchema = z.object({
  max_req_madrugada: z
    .number({ error: "Limite madrugada e obrigatorio" })
    .int()
    .min(1, "Minimo: 1")
    .max(700, "Maximo: 700")
    .default(590),
  max_req_dia: z
    .number({ error: "Limite dia e obrigatorio" })
    .int()
    .min(1, "Minimo: 1")
    .max(400, "Maximo: 400")
    .default(390),
  max_req_restrita: z
    .number({ error: "Limite restrita e obrigatorio" })
    .int()
    .min(1, "Minimo: 1")
    .max(180, "Maximo: 180")
    .default(170),
  velocidade_req_min: z
    .number({ error: "Velocidade e obrigatoria" })
    .int()
    .min(1, "Minimo: 1 req/min")
    .max(600, "Maximo: 600 req/min")
    .default(60),
  fuso_horario: z
    .string({ error: "Fuso horario e obrigatorio" })
    .min(1, "Fuso horario e obrigatorio")
    .default("America/Sao_Paulo"),
  tamanho_pagina: z
    .number({ error: "Tamanho de pagina e obrigatorio" })
    .int()
    .min(1, "Minimo: 1")
    .max(500, "Maximo: 500")
    .default(500),
});

// --- 5.4 Selecao de Endpoints (RN03) ---

const urlPattern = /^https?:\/\/.+/;

export const configEndpointsRequestSchema = z
  .object({
    baixar_despesas: z.boolean(),
    baixar_receitas: z.boolean(),
    base_url: z
      .string({ error: "URL base e obrigatoria" })
      .min(1, "URL base e obrigatoria")
      .regex(urlPattern, "URL deve iniciar com http:// ou https://")
      .default("https://api.portaldatransparencia.gov.br/api-de-dados"),
  })
  .superRefine((data, ctx) => {
    // RN03: Pelo menos 1 endpoint selecionado
    if (!data.baixar_despesas && !data.baixar_receitas) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Pelo menos um endpoint deve ser selecionado",
        path: ["baixar_despesas"],
      });
    }
  });

// --- 5.5 Configuracao de Saida (RN15) ---

export const configSaidaRequestSchema = z.object({
  diretorio_saida: z
    .string({ error: "Diretorio de saida e obrigatorio" })
    .min(1, "Diretorio de saida e obrigatorio"),
  formato_nome_arquivo: formatoNomeArquivoSchema,
  modo_escrita: modoEscritaSchema,
  diretorio_logs: z
    .string({ error: "Diretorio de logs e obrigatorio" })
    .min(1, "Diretorio de logs e obrigatorio"),
});

// --- 5.10 Retomada de Download (RN14) ---

export const resumeDownloadRequestSchema = z.object({
  endpoint_retomada: endpointTypeSchema,
  ano_retomada: z
    .number({ error: "Ano de retomada e obrigatorio" })
    .int()
    .min(2004, "Ano minimo: 2004")
    .max(2026, "Ano maximo: 2026"),
  mes_retomada: z
    .number({ error: "Mes de retomada e obrigatorio" })
    .int()
    .min(1, "Mes minimo: 1")
    .max(12, "Mes maximo: 12"),
  pagina_retomada: z
    .number({ error: "Pagina de retomada e obrigatoria" })
    .int()
    .min(1, "Pagina minima: 1"),
  ignorar_arquivos_existentes: z.boolean().default(false),
});

// --- 5.8 Visualizador de Logs (RN16) ---

export const logFiltersSchema = z
  .object({
    filtro_data_inicio: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, "Formato deve ser YYYY-MM-DD")
      .optional()
      .or(z.literal("")),
    filtro_data_fim: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, "Formato deve ser YYYY-MM-DD")
      .optional()
      .or(z.literal("")),
    filtro_nivel_log: z
      .enum(["todos", "info", "warning", "error"])
      .optional(),
    filtro_endpoint: z
      .enum(["todos", "despesas", "receitas"])
      .optional(),
    filtro_token: z
      .enum(["todos", "token_1", "token_2", "token_3"])
      .optional(),
    busca_texto: z
      .string()
      .optional()
      .or(z.literal("")),
    limit: z.number().int().positive().optional(),
    offset: z.number().int().min(0).optional(),
  })
  .superRefine((data, ctx) => {
    // RN16: Busca de texto exige minimo 3 caracteres
    if (data.busca_texto && data.busca_texto.length > 0 && data.busca_texto.length < 3) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Busca de texto deve ter no minimo 3 caracteres",
        path: ["busca_texto"],
      });
    }
    // filtro_data_fim >= filtro_data_inicio
    if (
      data.filtro_data_inicio &&
      data.filtro_data_fim &&
      data.filtro_data_inicio !== "" &&
      data.filtro_data_fim !== "" &&
      data.filtro_data_fim < data.filtro_data_inicio
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Data fim deve ser maior ou igual a data inicio",
        path: ["filtro_data_fim"],
      });
    }
  });

// --- 5.9 Progresso de Downloads ---

export const progressFiltersSchema = z.object({
  filtro_ano: z.number().int().min(2004).max(2026).optional(),
  filtro_endpoint: z
    .enum(["todos", "despesas", "receitas"])
    .optional(),
  exibir_apenas_pendentes: z.boolean().default(false),
});

// --- Inferred Types (para uso nos formularios) ---

export type ConfigTokensFormData = z.infer<typeof configTokensRequestSchema>;
export type ConfigPeriodoFormData = z.infer<typeof configPeriodoRequestSchema>;
export type ConfigRateLimitFormData = z.infer<typeof configRateLimitRequestSchema>;
export type ConfigEndpointsFormData = z.infer<typeof configEndpointsRequestSchema>;
export type ConfigSaidaFormData = z.infer<typeof configSaidaRequestSchema>;
export type ResumeDownloadFormData = z.infer<typeof resumeDownloadRequestSchema>;
export type LogFiltersFormData = z.infer<typeof logFiltersSchema>;
export type ProgressFiltersFormData = z.infer<typeof progressFiltersSchema>;

export const iaProviderSchema = z.enum(["gemini", "claude"]);

export const configIARequestSchema = z.object({
  gemini_api_key: z.string().or(z.literal("")),
  anthropic_api_key: z.string().or(z.literal("")),
  ia_provider: iaProviderSchema,
  ia_model: z.string().min(1, "O modelo da IA e obrigatorio").default("gemini-3.5-flash"),
});

export type ConfigIAFormData = z.infer<typeof configIARequestSchema>;

