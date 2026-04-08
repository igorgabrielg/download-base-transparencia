from fastapi import APIRouter, Query

from app.models.schemas import LogEntryResponse, LogFilters, LogListResponse, LogLevel

router = APIRouter()


@router.get("", response_model=LogListResponse)
async def get_logs(
    filtro_nivel_log: LogLevel | None = Query(None),
    filtro_endpoint: str | None = Query(None),
    filtro_token: str | None = Query(None),
    filtro_data_inicio: str | None = Query(None),
    filtro_data_fim: str | None = Query(None),
    busca_texto: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    # TODO: implementar leitura de logs
    return LogListResponse(items=[], total=0)
