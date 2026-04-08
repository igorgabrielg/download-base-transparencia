from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import config_router, download_router, logs_router, progress_router, ia_router
from app.core.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.diretorio_saida).mkdir(parents=True, exist_ok=True)
    Path(settings.diretorio_logs).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Download Base Transparencia",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config_router.router, prefix="/api/config", tags=["config"])
app.include_router(download_router.router, prefix="/api/download", tags=["download"])
app.include_router(logs_router.router, prefix="/api/logs", tags=["logs"])
app.include_router(progress_router.router, prefix="/api/progress", tags=["progress"])
app.include_router(ia_router.router, prefix="/api/ia", tags=["ia"])
app.include_router(ws_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
