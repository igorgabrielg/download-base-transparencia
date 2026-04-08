import asyncio
import logging
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings
from app.core.rate_limiter import RateLimiter
from app.core.websocket import manager as ws_manager
from app.models.schemas import (
    CheckpointStatus,
    DownloadStatus,
    EndpointType,
    ExecutionStatus,
    TokenId,
    TokenStatus,
    TokenStatusEnum,
)
from app.services.checkpoint_service import CheckpointService
from app.services.config_service import load_config
from app.services.csv_writer import CsvWriter
from app.services.sqlite_writer import SqliteWriter
from app.services.token_manager import TokenManager

logger = logging.getLogger(__name__)

ENDPOINT_PATHS = {
    "despesas": "/despesas/recursos-recebidos",
}

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2


class Downloader:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.token_manager = TokenManager(self.rate_limiter)
        self.csv_writer = CsvWriter()
        self.sqlite_writer = SqliteWriter()
        self.checkpoint_service = CheckpointService()
        self._running = False
        self._paused = False
        self._concluido = False
        self._current_endpoint: Optional[str] = None
        self._current_ano: int = 0
        self._current_mes: int = 0
        self._current_pagina: int = 0
        self._total_registros: int = 0
        self._mensagem: str = ""
        self._msg_seq: int = 0
        self._task: Optional[asyncio.Task] = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def get_status(self) -> DownloadStatus:
        if self._concluido:
            status = ExecutionStatus.concluido
        elif not self._running and not self._paused:
            status = ExecutionStatus.parado
        elif self._paused:
            status = ExecutionStatus.pausado
        else:
            status = ExecutionStatus.executando

        token = self.token_manager.get_active_token()
        token_id = None
        if token:
            try:
                token_id = TokenId(token["id"])
            except ValueError:
                pass

        endpoint_atual = None
        if self._current_endpoint:
            try:
                endpoint_atual = EndpointType(self._current_endpoint)
            except ValueError:
                pass

        ano_mes = None
        if self._current_ano and self._current_mes:
            ano_mes = f"{self._current_ano}/{self._current_mes:02d}"

        token_statuses = []
        for ts in self.token_manager.statuses:
            try:
                tid = TokenId(ts["token_id"])
            except ValueError:
                continue
            s = TokenStatusEnum.ativo if ts["ativo"] else TokenStatusEnum.invalido
            if ts["ativo"] and ts["requisicoes_restantes"] == 0:
                s = TokenStatusEnum.limite_atingido
            token_statuses.append(TokenStatus(
                token_id=tid,
                status=s,
                req_minuto_atual=ts["requisicoes"],
                limite_aplicavel=self.rate_limiter.get_current_limit(),
                tempo_para_reset=int(ts["janela_reset"]),
            ))

        return DownloadStatus(
            status=status,
            token_ativo=token_id,
            req_minuto=self.rate_limiter.requests_in_window,
            endpoint_atual=endpoint_atual,
            ano_mes_atual=ano_mes,
            pagina_atual=self._current_pagina,
            total_registros=self._total_registros,
            token_statuses=token_statuses,
            mensagem=self._mensagem,
            msg_seq=self._msg_seq,
        )

    async def _broadcast_status(self):
        status = self.get_status()
        await ws_manager.broadcast(status.model_dump(mode="json"))

    async def start(self, resume_endpoint: str | None = None,
                    resume_ano: int | None = None,
                    resume_mes: int | None = None,
                    resume_pagina: int | None = None,
                    ignorar_existentes: bool = False):
        if self._running:
            logger.warning("Download ja em execucao")
            return

        cfg = load_config()
        self.token_manager.reload_tokens([
            cfg.get("token_1", ""),
            cfg.get("token_2", ""),
            cfg.get("token_3", ""),
        ])
        self.rate_limiter.reload_config(
            velocidade=cfg.get("velocidade_req_min", settings.velocidade_req_min),
        )

        output_dir = cfg.get("diretorio_saida", str(settings.diretorio_saida))
        self.csv_writer.set_output_dir(output_dir)

        if not self.token_manager.has_active_tokens:
            logger.error("Nenhum token configurado")
            return

        self._running = True
        self._paused = False
        self._concluido = False
        self._total_registros = 0
        self._mensagem = "Iniciando download..."
        logger.info("Download iniciado")

        self._task = asyncio.create_task(
            self._download_loop(cfg, resume_endpoint, resume_ano,
                                resume_mes, resume_pagina, ignorar_existentes)
        )

    async def _download_loop(self, cfg: dict,
                             resume_endpoint: str | None = None,
                             resume_ano: int | None = None,
                             resume_mes: int | None = None,
                             resume_pagina: int | None = None,
                             ignorar_existentes: bool = False):
        try:
            endpoints = []
            if cfg.get("baixar_despesas", True):
                endpoints.append("despesas")

            ano_inicio = cfg.get("ano_inicio", settings.ano_inicio)
            ano_fim = cfg.get("ano_fim", settings.ano_fim)
            mes_inicio = cfg.get("mes_inicio", settings.mes_inicio)
            mes_fim = cfg.get("mes_fim", settings.mes_fim)
            tamanho_pagina = cfg.get("tamanho_pagina", settings.tamanho_pagina)
            base_url = cfg.get("base_url", settings.api_base_url)

            skip_until_found = resume_endpoint is not None

            async with httpx.AsyncClient(timeout=30.0) as client:
                for endpoint in endpoints:
                    if not self._running:
                        break

                    if skip_until_found and endpoint != resume_endpoint:
                        continue

                    for ano in range(ano_inicio, ano_fim + 1):
                        if not self._running:
                            break

                        for mes in range(1, 13):
                            if not self._running:
                                break

                            if ano == ano_inicio and mes < mes_inicio:
                                continue
                            if ano == ano_fim and mes > mes_fim:
                                continue

                            if skip_until_found:
                                if endpoint == resume_endpoint and ano == resume_ano and mes == resume_mes:
                                    skip_until_found = False
                                else:
                                    continue

                            start_page = 1
                            if resume_pagina and endpoint == resume_endpoint and ano == resume_ano and mes == resume_mes:
                                start_page = resume_pagina
                                resume_pagina = None
                            elif not ignorar_existentes:
                                existing = self.checkpoint_service.get_last(endpoint, ano, mes)
                                if existing and existing.status == CheckpointStatus.concluido:
                                    csv_file = f"{endpoint}_{ano}_{mes:02d}.csv"
                                    csv_path = Path(cfg.get("diretorio_saida", str(settings.diretorio_saida))) / csv_file
                                    if csv_path.exists():
                                        self._mensagem = f"{endpoint} {ano}/{mes:02d} ja baixado ({existing.total_registros} reg.) - pulando"
                                        self._msg_seq += 1
                                        self._current_endpoint = endpoint
                                        self._current_ano = ano
                                        self._current_mes = mes
                                        logger.info("Pulando %s %d/%02d (ja concluido)", endpoint, ano, mes)
                                        await self._broadcast_status()
                                        await asyncio.sleep(0.05)
                                        continue
                                    else:
                                        self._mensagem = f"{endpoint} {ano}/{mes:02d} marcado como concluido mas CSV ausente - baixando novamente"
                                        self._msg_seq += 1
                                        logger.warning("CSV ausente para %s %d/%02d, rebaixando", endpoint, ano, mes)
                                        await self._broadcast_status()
                                        await asyncio.sleep(0.05)

                            self._current_endpoint = endpoint
                            self._current_ano = ano
                            self._current_mes = mes

                            await self._download_period(
                                client, base_url, endpoint, ano, mes,
                                tamanho_pagina, start_page,
                            )

            if self._running:
                logger.info("Download concluido! Total: %d registros", self._total_registros)
                self._running = False
                self._concluido = True
                self._msg_seq += 1
                if self._total_registros > 0:
                    self._mensagem = f"Download concluido! {self._total_registros} registros baixados."
                else:
                    self._mensagem = "Todos os periodos ja foram baixados anteriormente. Nenhum novo download necessario."
                await self._broadcast_status()

        except Exception:
            logger.exception("Erro fatal no download loop")
            self._running = False
            await self._broadcast_status()

    async def _download_period(self, client: httpx.AsyncClient, base_url: str,
                               endpoint: str, ano: int, mes: int,
                               tamanho_pagina: int, start_page: int):
        pagina = start_page
        total_period = 0
        path = ENDPOINT_PATHS.get(endpoint, f"/{endpoint}")

        self._mensagem = f"Baixando {endpoint} {ano}/{mes:02d} (pagina {pagina})..."
        self._msg_seq += 1
        logger.info("Iniciando %s %d/%02d (pagina %d)", endpoint, ano, mes, pagina)

        from app.models.schemas import Checkpoint as CheckpointModel

        self.checkpoint_service.save(CheckpointModel(
            endpoint=EndpointType(endpoint),
            ano=ano,
            mes=mes,
            pagina=pagina,
            total_registros=0,
            status=CheckpointStatus.em_andamento,
            arquivo_csv=f"{endpoint}_{ano}_{mes:02d}.csv",
        ))

        while self._running:
            while self._paused:
                await asyncio.sleep(0.5)
                if not self._running:
                    return

            await self.rate_limiter.wait_if_needed()

            token = self.token_manager.get_available_token()
            if not token:
                if not self.token_manager.has_active_tokens:
                    logger.error("Todos os tokens invalidos. Parando.")
                    self._running = False
                    await self._broadcast_status()
                    return

                wait_time = self.token_manager.min_seconds_until_reset()
                active_count = len([t for t in self.token_manager._tokens if t["ativo"]])
                if active_count <= 1:
                    logger.warning(
                        "Limite de requisicoes atingido no unico token disponivel. "
                        "Aguardando %.0fs para nova janela...",
                        wait_time,
                    )
                else:
                    logger.warning(
                        "Todos os %d tokens atingiram o limite. "
                        "Aguardando %.0fs para nova janela...",
                        active_count, wait_time,
                    )
                await self._broadcast_status()
                await asyncio.sleep(wait_time + 1)
                continue

            self._current_pagina = pagina
            self._mensagem = ""
            await self._broadcast_status()

            data = await self._fetch_page(
                client, base_url, path, token, ano, mes, pagina, tamanho_pagina,
            )

            if data is None:
                self.checkpoint_service.save(CheckpointModel(
                    endpoint=EndpointType(endpoint),
                    ano=ano,
                    mes=mes,
                    pagina=pagina,
                    total_registros=total_period,
                    status=CheckpointStatus.erro,
                    arquivo_csv=f"{endpoint}_{ano}_{mes:02d}.csv",
                ))
                return

            if len(data) == 0:
                logger.info(
                    "Fim da paginacao %s %d/%02d: %d registros",
                    endpoint, ano, mes, total_period,
                )
                self.checkpoint_service.save(CheckpointModel(
                    endpoint=EndpointType(endpoint),
                    ano=ano,
                    mes=mes,
                    pagina=pagina,
                    total_registros=total_period,
                    status=CheckpointStatus.concluido,
                    arquivo_csv=f"{endpoint}_{ano}_{mes:02d}.csv",
                ))
                break

            self.csv_writer.write(data, endpoint, ano, mes)
            self.sqlite_writer.write(data, endpoint, ano, mes, pagina)
            total_period += len(data)
            self._total_registros += len(data)

            self.checkpoint_service.save(CheckpointModel(
                endpoint=EndpointType(endpoint),
                ano=ano,
                mes=mes,
                pagina=pagina,
                total_registros=total_period,
                status=CheckpointStatus.em_andamento,
                arquivo_csv=f"{endpoint}_{ano}_{mes:02d}.csv",
            ))

            await self._broadcast_status()

            if len(data) < tamanho_pagina:
                logger.info(
                    "Ultima pagina %s %d/%02d: %d registros",
                    endpoint, ano, mes, total_period,
                )
                self.checkpoint_service.save(CheckpointModel(
                    endpoint=EndpointType(endpoint),
                    ano=ano,
                    mes=mes,
                    pagina=pagina,
                    total_registros=total_period,
                    status=CheckpointStatus.concluido,
                    arquivo_csv=f"{endpoint}_{ano}_{mes:02d}.csv",
                ))
                break

            pagina += 1

    async def _fetch_page(self, client: httpx.AsyncClient, base_url: str,
                          path: str, token: dict, ano: int, mes: int,
                          pagina: int, tamanho_pagina: int) -> list[dict] | None:
        url = f"{base_url}{path}"
        mes_ano = f"{mes:02d}/{ano}"
        params = {
            "mesAnoInicio": mes_ano,
            "mesAnoFim": mes_ano,
            "pagina": pagina,
        }
        headers = {"chave-api-dados": token["value"]}

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.token_manager.record_request(token["id"])
                resp = await client.get(url, params=params, headers=headers)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code == 429:
                    logger.warning(
                        "HTTP 429 (rate limit) token %s. Rotacionando.",
                        token["id"],
                    )
                    self.token_manager.rotate()
                    next_token = self.token_manager.get_available_token()
                    if not next_token:
                        if not self.token_manager.has_active_tokens:
                            logger.error("Sem tokens disponiveis apos 429")
                            return None
                        wait_time = self.token_manager.min_seconds_until_reset()
                        logger.warning(
                            "Todos os tokens no limite apos 429. Aguardando %.0fs...",
                            wait_time,
                        )
                        await self._broadcast_status()
                        await asyncio.sleep(wait_time + 1)
                        next_token = self.token_manager.get_available_token()
                        if not next_token:
                            logger.error("Sem tokens disponiveis apos aguardar reset")
                            return None
                    token = next_token
                    headers = {"chave-api-dados": token["value"]}
                    await asyncio.sleep(2)
                    continue

                if resp.status_code in (401, 403):
                    logger.warning(
                        "HTTP %d (nao autorizado) token %s. Removendo.",
                        resp.status_code, token["id"],
                    )
                    self.token_manager.remove_token(token["id"])
                    token = self.token_manager.get_active_token()
                    if not token:
                        logger.error("Sem tokens disponiveis apos 401")
                        return None
                    headers = {"chave-api-dados": token["value"]}
                    continue

                if resp.status_code >= 500:
                    wait = RETRY_BACKOFF_BASE ** attempt
                    logger.warning(
                        "HTTP %d (server error). Tentativa %d/%d. Aguardando %ds.",
                        resp.status_code, attempt, MAX_RETRIES, wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                logger.error("HTTP %d inesperado: %s", resp.status_code, resp.text[:200])
                return None

            except httpx.TimeoutException:
                wait = RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "Timeout na requisicao. Tentativa %d/%d. Aguardando %ds.",
                    attempt, MAX_RETRIES, wait,
                )
                await asyncio.sleep(wait)
            except httpx.RequestError as exc:
                logger.error("Erro de rede: %s", str(exc))
                return None

        logger.error("Max retries atingido para pagina %d", pagina)
        return None

    async def pause(self):
        self._paused = True
        logger.info("Download pausado")
        await self._broadcast_status()

    async def resume(self):
        self._paused = False
        logger.info("Download retomado")
        await self._broadcast_status()

    async def stop(self):
        self._running = False
        self._paused = False
        self._concluido = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Download parado")
        await self._broadcast_status()


downloader = Downloader()
