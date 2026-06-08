import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

def get_config_file_path() -> Path:
    path = Path(settings.diretorio_saida) / "config.json"
    if path.exists():
        return path
    path_alt = Path("backend/data/config.json")
    if path_alt.exists():
        return path_alt
    return path


def _default_config() -> dict:
    return {
        "token_1": settings.token_1,
        "token_2": settings.token_2,
        "token_3": settings.token_3,
        "ano_inicio": settings.ano_inicio,
        "ano_fim": settings.ano_fim,
        "mes_inicio": settings.mes_inicio,
        "mes_fim": settings.mes_fim,
        "max_req_madrugada": settings.max_req_madrugada,
        "max_req_dia": settings.max_req_dia,
        "max_req_restrita": settings.max_req_restrita,
        "velocidade_req_min": settings.velocidade_req_min,
        "fuso_horario": settings.fuso_horario,
        "tamanho_pagina": settings.tamanho_pagina,
        "baixar_despesas": settings.baixar_despesas,
        "baixar_receitas": settings.baixar_receitas,
        "base_url": settings.api_base_url,
        "diretorio_saida": str(settings.diretorio_saida),
        "formato_nome_arquivo": settings.formato_nome_arquivo,
        "modo_escrita": settings.modo_escrita,
        "diretorio_logs": str(settings.diretorio_logs),
        "gemini_api_key": settings.gemini_api_key,
        "anthropic_api_key": settings.anthropic_api_key,
        "ia_provider": settings.ia_provider,
        "ia_model": settings.ia_model,
    }


def load_config() -> dict:
    config_file = get_config_file_path()
    if config_file.exists():
        try:
            return json.loads(config_file.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("Config corrompida, usando defaults")
    return _default_config()


def save_config(config: dict) -> dict:
    current = load_config()
    current.update(config)
    config_file = get_config_file_path()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(current, indent=2))
    logger.info("Config salva em %s", config_file)
    return current


def get_tokens() -> list[str]:
    cfg = load_config()
    return [t for t in [cfg.get("token_1", ""), cfg.get("token_2", ""), cfg.get("token_3", "")] if t]
