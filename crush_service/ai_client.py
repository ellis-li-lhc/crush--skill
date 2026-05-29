from __future__ import annotations

import logging
from typing import Any

import requests

from crush_service.config import AIConfig


LOGGER = logging.getLogger(__name__)


DEFAULT_PROVIDER_URLS = {
    "zhipu": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    "deepseek": "https://api.deepseek.com/v1/chat/completions",
    "openai": "https://api.openai.com/v1/chat/completions",
}


class AIClient:
    def __init__(self, config: AIConfig) -> None:
        self.config = config

    def generate_reply(self, messages: list[dict[str, str]]) -> str:
        payload = {"model": self.config.model, "messages": messages}
        response = requests.post(
            self._get_url(),
            headers=self._build_headers(),
            json=payload,
            timeout=self.config.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        LOGGER.debug("AI response body: %s", body)

        try:
            return body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"AI 返回格式不符合预期: {body}") from exc

    def _get_url(self) -> str:
        if self.config.base_url:
            return self.config.base_url
        provider = self.config.provider.lower()
        return DEFAULT_PROVIDER_URLS.get(provider, DEFAULT_PROVIDER_URLS["openai"])

    def _build_headers(self) -> dict[str, str]:
        provider = self.config.provider.lower()
        token = self.config.api_key
        if provider == "zhipu":
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
