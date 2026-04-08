from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    token_1: str = ""
    token_2: str = ""
    token_3: str = ""

    api_base_url: str = "https://api.portaldatransparencia.gov.br/api-de-dados"

    max_req_madrugada: int = 590
    max_req_dia: int = 390
    max_req_restrita: int = 170
    velocidade_req_min: int = 60

    ano_inicio: int = 2014
    ano_fim: int = 2026
    mes_inicio: int = 1
    mes_fim: int = 12

    tamanho_pagina: int = 500

    baixar_despesas: bool = True
    baixar_receitas: bool = True

    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    ia_provider: str = "gemini"
    ia_model: str = "gemini-3.5-flash"

    formato_nome_arquivo: str = "por_ano_mes"
    modo_escrita: str = "append"

    diretorio_saida: Path = Path("./data")
    diretorio_logs: Path = Path("./logs")

    fuso_horario: str = "America/Sao_Paulo"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def tokens(self) -> list[str]:
        return [t for t in [self.token_1, self.token_2, self.token_3] if t]


settings = Settings()
