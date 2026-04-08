from fastapi import APIRouter, HTTPException

from app.models.schemas import DownloadStatus, ResumeDownloadRequest
from app.services.downloader import downloader

router = APIRouter()


@router.post("/start", response_model=DownloadStatus)
async def start_download():
    if downloader.is_running:
        raise HTTPException(status_code=409, detail="Download ja em execucao")
    await downloader.start()
    return downloader.get_status()


@router.post("/pause", response_model=DownloadStatus)
async def pause_download():
    if not downloader.is_running:
        raise HTTPException(status_code=409, detail="Nenhum download em execucao")
    await downloader.pause()
    return downloader.get_status()


@router.post("/resume", response_model=DownloadStatus)
async def resume_download():
    if not downloader.is_paused:
        raise HTTPException(status_code=409, detail="Download nao esta pausado")
    await downloader.resume()
    return downloader.get_status()


@router.post("/stop", response_model=DownloadStatus)
async def stop_download():
    if not downloader.is_running and not downloader.is_paused:
        raise HTTPException(status_code=409, detail="Nenhum download em execucao")
    await downloader.stop()
    return downloader.get_status()


@router.post("/resume-from-checkpoint", response_model=DownloadStatus)
async def resume_from_checkpoint(data: ResumeDownloadRequest):
    if downloader.is_running:
        raise HTTPException(status_code=409, detail="Download ja em execucao")
    await downloader.start(
        resume_endpoint=data.endpoint_retomada.value,
        resume_ano=data.ano_retomada,
        resume_mes=data.mes_retomada,
        resume_pagina=data.pagina_retomada,
        ignorar_existentes=data.ignorar_arquivos_existentes,
    )
    return downloader.get_status()


@router.get("/status", response_model=DownloadStatus)
async def get_status():
    return downloader.get_status()
