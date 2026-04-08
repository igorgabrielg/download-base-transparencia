from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


# --- Enums ---

class EndpointType(str, Enum):
    despesas = "despesas"
    receitas = "receitas"


class IAProvider(str, Enum):
    gemini = "gemini"
    claude = "claude"


class CheckpointStatus(str, Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluido = "concluido"
    erro = "erro"
    arquivo_ausente = "arquivo_ausente"


class TokenStatusEnum(str, Enum):
    ativo = "ativo"
    em_espera = "em_espera"
    invalido = "invalido"
    limite_atingido = "limite_atingido"


class LogLevel(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class ExecutionStatus(str, Enum):
    parado = "parado"
    executando = "executando"
    pausado = "pausado"
    erro = "erro"
    concluido = "concluido"


class FormatoNomeArquivo(str, Enum):
    por_ano_mes = "por_ano_mes"
    por_ano = "por_ano"


class ModoEscrita(str, Enum):
    append = "append"
    overwrite = "overwrite"


class TokenId(str, Enum):
    token_1 = "token_1"
    token_2 = "token_2"
    token_3 = "token_3"


class TokenValidationStatus(str, Enum):
    valido = "valido"
    invalido = "invalido"
    nao_testado = "nao_testado"


# --- 4.1 Config (config.json) ---

class Config(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    token_1: str = ""
    token_2: str = ""
    token_3: str = ""
    ano_inicio: int = Field(default=2014, ge=2004, le=2026)
    ano_fim: int = Field(default=2026, ge=2004, le=2026)
    mes_inicio: int = Field(default=1, ge=1, le=12)
    mes_fim: int = Field(default=12, ge=1, le=12)
    max_req_madrugada: int = Field(default=590, ge=1, le=700)
    max_req_dia: int = Field(default=390, ge=1, le=400)
    max_req_restrita: int = Field(default=170, ge=1, le=180)
    velocidade_req_min: int = Field(default=60, ge=1, le=600)
    fuso_horario: str = "America/Sao_Paulo"
    tamanho_pagina: int = Field(default=500, ge=1, le=500)
    baixar_despesas: bool = True
    baixar_receitas: bool = True
    base_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"
    diretorio_saida: str = "./data"
    formato_nome_arquivo: FormatoNomeArquivo = FormatoNomeArquivo.por_ano_mes
    modo_escrita: ModoEscrita = ModoEscrita.append
    diretorio_logs: str = "./logs"
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    ia_provider: IAProvider = IAProvider.gemini
    ia_model: str = "gemini-3.5-flash"
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def validate_period(self):
        if self.ano_fim < self.ano_inicio:
            raise ValueError("ano_fim deve ser >= ano_inicio")
        if self.ano_inicio == self.ano_fim and self.mes_fim < self.mes_inicio:
            raise ValueError("mes_fim deve ser >= mes_inicio quando no mesmo ano")
        return self

    @model_validator(mode="after")
    def validate_endpoints(self):
        if not self.baixar_despesas and not self.baixar_receitas:
            raise ValueError("Pelo menos um endpoint deve ser selecionado")
        return self

    @model_validator(mode="after")
    def validate_tokens_unique(self):
        tokens = [t for t in [self.token_1, self.token_2, self.token_3] if t]
        if len(tokens) != len(set(tokens)):
            raise ValueError("Tokens duplicados nao sao permitidos")
        return self

    @property
    def tokens(self) -> list[str]:
        return [t for t in [self.token_1, self.token_2, self.token_3] if t]


# --- Config Request/Response models ---

class ConfigIARequest(BaseModel):
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    ia_provider: IAProvider
    ia_model: str = "gemini-3.5-flash"


class ConfigIAResponse(BaseModel):
    gemini_api_key: str
    anthropic_api_key: str
    ia_provider: IAProvider
    ia_model: str

class ConfigTokensRequest(BaseModel):
    token_1: str
    token_2: str = ""
    token_3: str = ""
    validar_tokens: bool = False

    @field_validator("token_1")
    @classmethod
    def token_1_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("token_1 e obrigatorio")
        return v.strip()

    @model_validator(mode="after")
    def validate_unique(self):
        tokens = [t for t in [self.token_1, self.token_2, self.token_3] if t]
        if len(tokens) != len(set(tokens)):
            raise ValueError("Tokens duplicados nao sao permitidos")
        return self


class TokenValidationResult(BaseModel):
    token_id: TokenId
    status: TokenValidationStatus
    message: str = ""


class ConfigTokensResponse(BaseModel):
    token_1: str
    token_2: str
    token_3: str
    validations: list[TokenValidationResult] = []


class ConfigPeriodoRequest(BaseModel):
    ano_inicio: int = Field(ge=2004, le=2026)
    ano_fim: int = Field(ge=2004, le=2026)
    mes_inicio: int = Field(default=1, ge=1, le=12)
    mes_fim: int = Field(default=12, ge=1, le=12)

    @model_validator(mode="after")
    def validate_period(self):
        if self.ano_fim < self.ano_inicio:
            raise ValueError("ano_fim deve ser >= ano_inicio")
        if self.ano_inicio == self.ano_fim and self.mes_fim < self.mes_inicio:
            raise ValueError("mes_fim deve ser >= mes_inicio quando no mesmo ano")
        return self


class ConfigPeriodoResponse(BaseModel):
    ano_inicio: int
    ano_fim: int
    mes_inicio: int
    mes_fim: int
    total_meses: int


class ConfigRateLimitRequest(BaseModel):
    max_req_madrugada: int = Field(ge=1, le=700)
    max_req_dia: int = Field(ge=1, le=400)
    max_req_restrita: int = Field(ge=1, le=180)
    velocidade_req_min: int = Field(default=60, ge=1, le=600)
    fuso_horario: str = "America/Sao_Paulo"
    tamanho_pagina: int = Field(default=500, ge=1, le=500)


class ConfigRateLimitResponse(BaseModel):
    max_req_madrugada: int
    max_req_dia: int
    max_req_restrita: int
    velocidade_req_min: int
    fuso_horario: str
    tamanho_pagina: int


class ConfigEndpointsRequest(BaseModel):
    baixar_despesas: bool
    baixar_receitas: bool
    base_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"

    @model_validator(mode="after")
    def validate_at_least_one(self):
        if not self.baixar_despesas and not self.baixar_receitas:
            raise ValueError("Pelo menos um endpoint deve ser selecionado")
        return self


class ConfigEndpointsResponse(BaseModel):
    baixar_despesas: bool
    baixar_receitas: bool
    base_url: str


class ConfigSaidaRequest(BaseModel):
    diretorio_saida: str
    formato_nome_arquivo: FormatoNomeArquivo
    modo_escrita: ModoEscrita
    diretorio_logs: str = ""


class ConfigSaidaResponse(BaseModel):
    diretorio_saida: str
    formato_nome_arquivo: FormatoNomeArquivo
    modo_escrita: ModoEscrita
    diretorio_logs: str


class ConfigResponse(BaseModel):
    id: UUID
    tokens_count: int
    token_1: str = ""
    token_2: str = ""
    token_3: str = ""
    token_1_set: bool
    token_2_set: bool
    token_3_set: bool
    ano_inicio: int
    ano_fim: int
    mes_inicio: int
    mes_fim: int
    max_req_madrugada: int
    max_req_dia: int
    max_req_restrita: int
    velocidade_req_min: int
    fuso_horario: str
    tamanho_pagina: int
    baixar_despesas: bool
    baixar_receitas: bool
    base_url: str
    diretorio_saida: str
    formato_nome_arquivo: FormatoNomeArquivo
    modo_escrita: ModoEscrita
    diretorio_logs: str
    gemini_api_key: str
    anthropic_api_key: str
    ia_provider: IAProvider
    ia_model: str
    active: bool
    created_at: datetime
    last_update: datetime


# --- 4.2 Checkpoint ---

class Checkpoint(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    endpoint: EndpointType
    ano: int = Field(ge=2004, le=2026)
    mes: int = Field(ge=1, le=12)
    pagina: int = Field(ge=1)
    total_registros: int = Field(default=0, ge=0)
    status: CheckpointStatus = CheckpointStatus.pendente
    arquivo_csv: str = ""
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)


# --- 4.3 LogEntry ---

class LogEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    nivel: LogLevel
    token_id: TokenId | None = None
    endpoint: EndpointType | None = None
    ano: int | None = None
    mes: int | None = None
    pagina: int | None = None
    status_http: int | None = None
    mensagem: str = ""
    registros_obtidos: int | None = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)


class LogFilters(BaseModel):
    filtro_data_inicio: str | None = None
    filtro_data_fim: str | None = None
    filtro_nivel_log: LogLevel | None = None
    filtro_endpoint: EndpointType | None = None
    filtro_token: TokenId | None = None
    busca_texto: str | None = None
    limit: int = 100
    offset: int = 0

    @field_validator("busca_texto")
    @classmethod
    def validate_search_min_length(cls, v: str | None) -> str | None:
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Busca de texto exige minimo 3 caracteres")
        return v


class LogEntryResponse(BaseModel):
    id: UUID
    timestamp: datetime
    nivel: LogLevel
    token_id: TokenId | None
    endpoint: EndpointType | None
    ano: int | None
    mes: int | None
    pagina: int | None
    status_http: int | None
    mensagem: str
    registros_obtidos: int | None


class LogListResponse(BaseModel):
    items: list[LogEntryResponse]
    total: int


# --- 4.4 TokenStatus (runtime) ---

class TokenStatus(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    token_id: TokenId
    status: TokenStatusEnum = TokenStatusEnum.ativo
    req_minuto_atual: int = 0
    limite_aplicavel: int = 390
    janela_inicio: datetime | None = None
    tempo_para_reset: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)


# --- 4.5 DownloadProgress (derived from checkpoints) ---

class DownloadProgress(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    endpoint: EndpointType
    ano: int
    mes: int
    status: CheckpointStatus = CheckpointStatus.pendente
    arquivo_csv: str = ""
    tamanho_arquivo: int = 0
    total_registros: int = 0
    ultima_pagina: int = 0
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_update: datetime = Field(default_factory=datetime.now)


class ProgressFilters(BaseModel):
    filtro_ano: int | None = None
    filtro_endpoint: EndpointType | None = None
    exibir_apenas_pendentes: bool = False


class ProgressListResponse(BaseModel):
    items: list[DownloadProgress]
    total_arquivos_gerados: int
    tamanho_total_disco: int
    percentual_concluido: float


# --- Execution (Painel de Execucao) ---

class DownloadStatus(BaseModel):
    status: ExecutionStatus = ExecutionStatus.parado
    token_ativo: TokenId | None = None
    req_minuto: int = 0
    endpoint_atual: EndpointType | None = None
    ano_mes_atual: str | None = None
    pagina_atual: int = 0
    total_registros: int = 0
    token_statuses: list[TokenStatus] = []
    mensagem: str = ""
    msg_seq: int = 0


# --- Retomada de Download ---

class ResumeDownloadRequest(BaseModel):
    endpoint_retomada: EndpointType
    ano_retomada: int = Field(ge=2004, le=2026)
    mes_retomada: int = Field(ge=1, le=12)
    pagina_retomada: int = Field(ge=1)
    ignorar_arquivos_existentes: bool = False


class CheckpointListResponse(BaseModel):
    items: list[Checkpoint]


# --- Chat RAG ---

class ChatRequest(BaseModel):
    pergunta: str


class ChatResponse(BaseModel):
    resposta: str
    contexto: list[str] = []

