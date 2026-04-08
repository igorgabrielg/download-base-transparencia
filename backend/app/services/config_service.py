import json
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(settings.diretorio_saida) / "config.json"


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
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("Config corrompida, usando defaults")
    return _default_config()


def save_config(config: dict) -> dict:
    current = load_config()
    current.update(config)
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(current, indent=2))
    logger.info("Config salva em %s", CONFIG_FILE)
    return current


def get_tokens() -> list[str]:
    cfg = load_config()
    return [t for t in [cfg.get("token_1", ""), cfg.get("token_2", ""), cfg.get("token_3", "")] if t]
