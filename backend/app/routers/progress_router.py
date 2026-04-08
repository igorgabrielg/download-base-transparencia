import os
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Query

from app.config import settings
from app.models.schemas import (
    Checkpoint,
    CheckpointListResponse,
    CheckpointStatus,
    DownloadProgress,
    EndpointType,
    ProgressListResponse,
)
from app.services.checkpoint_service import CheckpointService
from app.services.config_service import load_config

router = APIRouter()

checkpoint_service = CheckpointService()


def _load_sqlite_records(db_path: Path) -> dict[str, int]:
    """Carrega contagem de registros por endpoint/ano/mes do SQLite."""
    records: dict[str, int] = {}
    if not db_path.exists():
        return records
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        for (table_name,) in tables:
            try:
                rows = cursor.execute(
                    f'SELECT _ano, _mes, COUNT(*) FROM "{table_name}" GROUP BY _ano, _mes'
                ).fetchall()
                for ano, mes, count in rows:
                    key = f"{table_name}_{ano}_{mes}"
                    records[key] = count
            except sqlite3.OperationalError:
                continue
        conn.close()
    except Exception:
        pass
    return records


@router.get("", response_model=ProgressListResponse)
async def get_progress(
    filtro_endpoint: str | None = Query(None),
    filtro_ano: int | None = Query(None),
    exibir_apenas_pendentes: bool = Query(False),
):
    cfg = load_config()
    output_dir = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida)))
    db_path = Path("./data") / "transparencia.db"

    checkpoints = checkpoint_service.load_all()
    sqlite_records = _load_sqlite_records(db_path)

    # Periodo configurado para download
    cfg_ano_inicio = cfg.get("ano_inicio", settings.ano_inicio)
    cfg_ano_fim = cfg.get("ano_fim", settings.ano_fim)
    cfg_mes_inicio = cfg.get("mes_inicio", settings.mes_inicio)
    cfg_mes_fim = cfg.get("mes_fim", settings.mes_fim)

    # Descobrir range total: desde 2014 ate ano/mes atual
    now = datetime.now()
    ano_inicio = 2014
    ano_fim = now.year
    mes_fim_global = now.month

    endpoints_cfg = []
    if cfg.get("baixar_despesas", settings.baixar_despesas):
        endpoints_cfg.append("despesas")
    if cfg.get("baixar_receitas", settings.baixar_receitas):
        endpoints_cfg.append("receitas")

    # Se nenhum endpoint configurado, mostrar despesas como default
    if not endpoints_cfg:
        endpoints_cfg = ["despesas"]

    items: list[DownloadProgress] = []
    total_arquivos = 0
    tamanho_total = 0
    total_slots = 0
    concluidos = 0

    for endpoint in endpoints_cfg:
        for ano in range(ano_inicio, ano_fim + 1):
            for mes in range(1, 13):
                # Nao mostrar meses futuros
                if ano == ano_fim and mes > mes_fim_global:
                    continue

                total_slots += 1
                key = f"{endpoint}_{ano}_{mes}"
                cp_data = checkpoints.get(key)
                registros_sqlite = sqlite_records.get(key, 0)

                status = CheckpointStatus.pendente
                total_registros = 0
                arquivo_csv = f"{endpoint}_{ano}_{mes:02d}.csv"
                tamanho_arquivo = 0
                ultima_pagina = 0

                if cp_data:
                    status = CheckpointStatus(cp_data.get("status", "pendente"))
                    total_registros = cp_data.get("total_registros", 0)
                    arquivo_csv = cp_data.get("arquivo_csv", arquivo_csv)
                    ultima_pagina = cp_data.get("pagina", 0)

                # Se nao tem checkpoint mas tem dados no SQLite
                if status == CheckpointStatus.pendente and registros_sqlite > 0:
                    status = CheckpointStatus.concluido
                    total_registros = registros_sqlite

                # Usar contagem do SQLite se disponivel e maior
                if registros_sqlite > total_registros:
                    total_registros = registros_sqlite

                csv_path = output_dir / arquivo_csv
                csv_exists = csv_path.exists()

                if csv_exists:
                    tamanho_arquivo = os.path.getsize(csv_path)
                    tamanho_total += tamanho_arquivo
                    total_arquivos += 1

                # Baixado (banco sabe) mas CSV nao esta na pasta
                if status == CheckpointStatus.concluido and not csv_exists:
                    status = CheckpointStatus.arquivo_ausente

                if status in (CheckpointStatus.concluido, CheckpointStatus.arquivo_ausente):
                    concluidos += 1

                if filtro_endpoint and endpoint != filtro_endpoint:
                    continue
                if filtro_ano and ano != filtro_ano:
                    continue
                if exibir_apenas_pendentes and status != CheckpointStatus.pendente:
                    continue

                items.append(DownloadProgress(
                    endpoint=EndpointType(endpoint),
                    ano=ano,
                    mes=mes,
                    status=status,
                    arquivo_csv=arquivo_csv,
                    tamanho_arquivo=tamanho_arquivo,
                    total_registros=total_registros,
                    ultima_pagina=ultima_pagina,
                ))

    percentual = (concluidos / total_slots * 100) if total_slots > 0 else 0.0

    return ProgressListResponse(
        items=items,
        total_arquivos_gerados=total_arquivos,
        tamanho_total_disco=tamanho_total,
        percentual_concluido=round(percentual, 2),
    )


@router.get("/checkpoints", response_model=CheckpointListResponse)
async def get_checkpoints():
    checkpoints = checkpoint_service.load_all()
    items = []
    for data in checkpoints.values():
        try:
            items.append(Checkpoint(**data))
        except Exception:
            continue
    return CheckpointListResponse(items=items)
