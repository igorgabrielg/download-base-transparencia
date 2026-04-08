from datetime import datetime
from uuid import uuid4

import httpx
from fastapi import APIRouter

from app.config import settings
from app.models.schemas import (
    ConfigEndpointsRequest,
    ConfigEndpointsResponse,
    ConfigPeriodoRequest,
    ConfigPeriodoResponse,
    ConfigRateLimitRequest,
    ConfigRateLimitResponse,
    ConfigResponse,
    ConfigSaidaRequest,
    ConfigSaidaResponse,
    ConfigTokensRequest,
    ConfigTokensResponse,
    TokenId,
    TokenValidationResult,
    TokenValidationStatus,
    IAProvider,
    ConfigIARequest,
    ConfigIAResponse,
)
from app.services.config_service import load_config, save_config

router = APIRouter()


@router.get("", response_model=ConfigResponse)
async def get_config():
    cfg = load_config()
    return ConfigResponse(
        id=uuid4(),
        tokens_count=len([t for t in [cfg.get("token_1", ""), cfg.get("token_2", ""), cfg.get("token_3", "")] if t]),
        token_1=cfg.get("token_1", ""),
        token_2=cfg.get("token_2", ""),
        token_3=cfg.get("token_3", ""),
        token_1_set=bool(cfg.get("token_1")),
        token_2_set=bool(cfg.get("token_2")),
        token_3_set=bool(cfg.get("token_3")),
        ano_inicio=cfg.get("ano_inicio", settings.ano_inicio),
        ano_fim=cfg.get("ano_fim", settings.ano_fim),
        mes_inicio=cfg.get("mes_inicio", settings.mes_inicio),
        mes_fim=cfg.get("mes_fim", settings.mes_fim),
        max_req_madrugada=cfg.get("max_req_madrugada", settings.max_req_madrugada),
        max_req_dia=cfg.get("max_req_dia", settings.max_req_dia),
        max_req_restrita=cfg.get("max_req_restrita", settings.max_req_restrita),
        velocidade_req_min=cfg.get("velocidade_req_min", settings.velocidade_req_min),
        fuso_horario=cfg.get("fuso_horario", settings.fuso_horario),
        tamanho_pagina=cfg.get("tamanho_pagina", settings.tamanho_pagina),
        baixar_despesas=cfg.get("baixar_despesas", True),
        baixar_receitas=cfg.get("baixar_receitas", True),
        base_url=cfg.get("base_url", settings.api_base_url),
        diretorio_saida=cfg.get("diretorio_saida", str(settings.diretorio_saida)),
        formato_nome_arquivo=cfg.get("formato_nome_arquivo", settings.formato_nome_arquivo),
        modo_escrita=cfg.get("modo_escrita", settings.modo_escrita),
        diretorio_logs=cfg.get("diretorio_logs", str(settings.diretorio_logs)),
        gemini_api_key=cfg.get("gemini_api_key", ""),
        anthropic_api_key=cfg.get("anthropic_api_key", ""),
        ia_provider=cfg.get("ia_provider", "gemini"),
        ia_model=cfg.get("ia_model", "gemini-3.5-flash"),
        active=True,
        created_at=datetime.now(),
        last_update=datetime.now(),
    )


@router.put("/tokens", response_model=ConfigTokensResponse)
async def update_tokens(data: ConfigTokensRequest):
    save_config({
        "token_1": data.token_1,
        "token_2": data.token_2,
        "token_3": data.token_3,
    })

    validations = []
    if data.validar_tokens:
        validations = await _validate_tokens_online(data.token_1, data.token_2, data.token_3)

    return ConfigTokensResponse(
        token_1=data.token_1,
        token_2=data.token_2,
        token_3=data.token_3,
        validations=validations,
    )


@router.post("/tokens/validate", response_model=list[TokenValidationResult])
async def validate_tokens():
    cfg = load_config()
    return await _validate_tokens_online(
        cfg.get("token_1", ""),
        cfg.get("token_2", ""),
        cfg.get("token_3", ""),
    )


async def _validate_tokens_online(token_1: str, token_2: str, token_3: str) -> list[TokenValidationResult]:
    results = []
    tokens = [
        (TokenId.token_1, token_1),
        (TokenId.token_2, token_2),
        (TokenId.token_3, token_3),
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for token_id, token_value in tokens:
            if not token_value:
                results.append(TokenValidationResult(
                    token_id=token_id,
                    status=TokenValidationStatus.nao_testado,
                    message="Token nao configurado",
                ))
                continue

            try:
                resp = await client.get(
                    f"{settings.api_base_url}/despesas",
                    params={"pagina": 1, "tamanhoPagina": 1},
                    headers={"chave-api-dados": token_value},
                )
                if resp.status_code == 200:
                    results.append(TokenValidationResult(
                        token_id=token_id,
                        status=TokenValidationStatus.valido,
                        message="Token valido",
                    ))
                elif resp.status_code in (401, 403):
                    results.append(TokenValidationResult(
                        token_id=token_id,
                        status=TokenValidationStatus.invalido,
                        message="Token invalido ou expirado",
                    ))
                else:
                    results.append(TokenValidationResult(
                        token_id=token_id,
                        status=TokenValidationStatus.invalido,
                        message=f"HTTP {resp.status_code}",
                    ))
            except httpx.RequestError as exc:
                results.append(TokenValidationResult(
                    token_id=token_id,
                    status=TokenValidationStatus.invalido,
                    message=f"Erro de conexao: {exc}",
                ))

    return results


@router.put("/periodo", response_model=ConfigPeriodoResponse)
async def update_periodo(data: ConfigPeriodoRequest):
    save_config({
        "ano_inicio": data.ano_inicio,
        "ano_fim": data.ano_fim,
        "mes_inicio": data.mes_inicio,
        "mes_fim": data.mes_fim,
    })
    total = (data.ano_fim - data.ano_inicio) * 12 + (data.mes_fim - data.mes_inicio + 1)
    return ConfigPeriodoResponse(
        ano_inicio=data.ano_inicio,
        ano_fim=data.ano_fim,
        mes_inicio=data.mes_inicio,
        mes_fim=data.mes_fim,
        total_meses=total,
    )


@router.put("/rate-limit", response_model=ConfigRateLimitResponse)
async def update_rate_limit(data: ConfigRateLimitRequest):
    save_config(data.model_dump())
    return ConfigRateLimitResponse(**data.model_dump())


@router.put("/endpoints", response_model=ConfigEndpointsResponse)
async def update_endpoints(data: ConfigEndpointsRequest):
    save_config(data.model_dump())
    return ConfigEndpointsResponse(**data.model_dump())


@router.put("/saida", response_model=ConfigSaidaResponse)
async def update_saida(data: ConfigSaidaRequest):
    save_config(data.model_dump())
    return ConfigSaidaResponse(**data.model_dump())


@router.put("/ia", response_model=ConfigIAResponse)
async def update_ia(data: ConfigIARequest):
    save_config(data.model_dump())
    return ConfigIAResponse(**data.model_dump())


@router.post("/pick-directory")
async def pick_directory():
    """Abre o seletor de pastas nativo do sistema operacional."""
    import platform
    import subprocess

    system = platform.system()

    try:
        if system == "Darwin":
            result = subprocess.run(
                ["osascript", "-e",
                 'POSIX path of (choose folder with prompt "Selecionar pasta de saida")'],
                capture_output=True, text=True, timeout=120,
            )
        elif system == "Windows":
            ps_script = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$f.Description = 'Selecionar pasta de saida'; "
                "if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath } else { '' }"
            )
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, text=True, timeout=120,
            )
        else:
            result = subprocess.run(
                ["zenity", "--file-selection", "--directory",
                 "--title=Selecionar pasta de saida"],
                capture_output=True, text=True, timeout=120,
            )

        path = result.stdout.strip().rstrip("/")
        if result.returncode == 0 and path:
            return {"path": path, "error": None}
        return {"path": "", "error": "Nenhuma pasta selecionada"}

    except FileNotFoundError:
        return {"path": "", "error": "Seletor de pastas nao disponivel neste sistema"}
    except subprocess.TimeoutExpired:
        return {"path": "", "error": "Timeout ao abrir seletor"}
    except Exception as exc:
        return {"path": "", "error": str(exc)}
