import time
import logging

from app.config import settings
from app.core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class TokenManager:
    def __init__(self, rate_limiter: RateLimiter):
        self._tokens: list[dict] = []
        self._current_index: int = 0
        self.rate_limiter = rate_limiter
        self._init_tokens()

    def _init_tokens(self):
        for i, token in enumerate(settings.tokens):
            self._tokens.append({
                "id": f"token_{i + 1}",
                "value": token,
                "ativo": True,
                "requisicoes": 0,
                "janela_inicio": time.time(),
            })

    def reload_tokens(self, tokens: list[str]):
        self._tokens.clear()
        self._current_index = 0
        for i, token in enumerate(tokens):
            if token:
                self._tokens.append({
                    "id": f"token_{i + 1}",
                    "value": token,
                    "ativo": True,
                    "requisicoes": 0,
                    "janela_inicio": time.time(),
                })

    def get_active_token(self) -> dict | None:
        ativos = [t for t in self._tokens if t["ativo"]]
        if not ativos:
            return None
        self._current_index = self._current_index % len(ativos)
        return ativos[self._current_index]

    def get_available_token(self) -> dict | None:
        """Retorna um token ativo que ainda tem requisicoes disponiveis.
        Se o token atual atingiu o limite, rotaciona para o proximo.
        Retorna None se todos os tokens ativos atingiram o limite."""
        ativos = [t for t in self._tokens if t["ativo"]]
        if not ativos:
            return None

        limite = self.rate_limiter.get_current_limit()

        for _ in range(len(ativos)):
            self._current_index = self._current_index % len(ativos)
            token = ativos[self._current_index]
            elapsed = time.time() - token["janela_inicio"]
            if elapsed >= 60:
                token["requisicoes"] = 0
                token["janela_inicio"] = time.time()
            if token["requisicoes"] < limite:
                return token
            logger.info(
                "Token %s atingiu limite (%d/%d). Tentando proximo...",
                token["id"], token["requisicoes"], limite,
            )
            self._current_index += 1

        return None

    def all_tokens_at_limit(self) -> bool:
        """Verifica se todos os tokens ativos atingiram o limite da janela."""
        ativos = [t for t in self._tokens if t["ativo"]]
        if not ativos:
            return True
        limite = self.rate_limiter.get_current_limit()
        for t in ativos:
            elapsed = time.time() - t["janela_inicio"]
            if elapsed >= 60:
                return False
            if t["requisicoes"] < limite:
                return False
        return True

    def min_seconds_until_reset(self) -> float:
        """Retorna o menor tempo ate reset de janela entre tokens ativos."""
        ativos = [t for t in self._tokens if t["ativo"]]
        if not ativos:
            return 0
        return min(max(0, 60 - (time.time() - t["janela_inicio"])) for t in ativos)

    def record_request(self, token_id: str):
        for t in self._tokens:
            if t["id"] == token_id:
                elapsed = time.time() - t["janela_inicio"]
                if elapsed >= 60:
                    t["requisicoes"] = 0
                    t["janela_inicio"] = time.time()
                t["requisicoes"] += 1
                break
        self.rate_limiter.record_request()

    def rotate(self):
        self._current_index += 1
        logger.info("Token rotacionado para index %d", self._current_index)

    def remove_token(self, token_id: str):
        for t in self._tokens:
            if t["id"] == token_id:
                t["ativo"] = False
                logger.warning("Token %s removido (invalido)", token_id)
                break

    def reset_window(self, token_id: str):
        for t in self._tokens:
            if t["id"] == token_id:
                t["requisicoes"] = 0
                t["janela_inicio"] = time.time()
                break

    @property
    def has_active_tokens(self) -> bool:
        return any(t["ativo"] for t in self._tokens)

    @property
    def statuses(self) -> list[dict]:
        limite = self.rate_limiter.get_current_limit()
        return [
            {
                "token_id": t["id"],
                "ativo": t["ativo"],
                "requisicoes": t["requisicoes"],
                "requisicoes_restantes": max(0, limite - t["requisicoes"]),
                "janela_reset": max(0, 60 - (time.time() - t["janela_inicio"])),
            }
            for t in self._tokens
        ]
