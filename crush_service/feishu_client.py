from __future__ import annotations

import json
import logging

import requests

from crush_service.config import FeishuConfig


LOGGER = logging.getLogger(__name__)


class FeishuClient:
    def __init__(self, config: FeishuConfig) -> None:
        self.config = config

    def get_token(self) -> str:
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        payload = {"app_id": self.config.app_id, "app_secret": self.config.app_secret}
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        body = response.json()
        if body.get("code") != 0:
            raise ValueError(f"获取飞书 token 失败: {body}")
        return body["app_access_token"]

    def send_text_message(self, token: str, receive_id: str, content: str) -> dict:
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        params = {"receive_id_type": "open_id"}
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": content}, ensure_ascii=False),
        }
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        body = response.json()
        LOGGER.debug("Feishu send response: %s", body)
        return body
