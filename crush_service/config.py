from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "config.json"
DEFAULT_ENV_PATH = ROOT_DIR / ".env"


@dataclass
class FeishuConfig:
    app_id: str
    app_secret: str
    webhook_url: str = ""


@dataclass
class AIConfig:
    provider: str
    api_key: str
    model: str
    base_url: str = ""
    timeout_seconds: int = 30


@dataclass
class PersonalityConfig:
    path: str


@dataclass
class AppConfig:
    feishu: FeishuConfig
    ai: AIConfig
    personality: PersonalityConfig
    crush_name: str = "小樱"
    default_stage: str = "陌生"
    database_path: str = "./data/crush.db"
    host: str = "0.0.0.0"
    port: int = 5001
    log_level: str = "INFO"


def load_dotenv(env_path: Path = DEFAULT_ENV_PATH) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _prune_empty_values(data: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested = _prune_empty_values(value)
            if nested:
                cleaned[key] = nested
        elif value not in ("", None):
            cleaned[key] = value
    return cleaned


def _load_file_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def _load_env_config() -> dict[str, Any]:
    return {
        "feishu": {
            "app_id": os.getenv("FEISHU_APP_ID", ""),
            "app_secret": os.getenv("FEISHU_APP_SECRET", ""),
            "webhook_url": os.getenv("FEISHU_WEBHOOK_URL", ""),
        },
        "ai": {
            "provider": os.getenv("AI_PROVIDER", ""),
            "api_key": os.getenv("AI_API_KEY", ""),
            "model": os.getenv("AI_MODEL", ""),
            "base_url": os.getenv("AI_BASE_URL", ""),
            "timeout_seconds": os.getenv("AI_TIMEOUT_SECONDS", ""),
        },
        "personality": {
            "path": os.getenv("PERSONALITY_PATH", ""),
        },
        "crush_name": os.getenv("CRUSH_NAME", ""),
        "default_stage": os.getenv("CURRENT_STAGE", ""),
        "database_path": os.getenv("DATABASE_PATH", ""),
        "host": os.getenv("APP_HOST", ""),
        "port": os.getenv("APP_PORT", ""),
        "log_level": os.getenv("LOG_LEVEL", ""),
    }


def _pick_str(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key)
    if value in (None, ""):
        return default
    return str(value)


def _pick_int(data: dict[str, Any], key: str, default: int) -> int:
    value = data.get(key)
    if value in (None, ""):
        return default
    return int(value)


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    load_dotenv()
    file_config = _load_file_config(config_path)
    env_config = _prune_empty_values(_load_env_config())
    raw = _deep_merge(file_config, env_config)
    if "default_stage" not in raw and raw.get("current_stage"):
        raw["default_stage"] = raw["current_stage"]

    feishu_raw = raw.get("feishu", {})
    ai_raw = raw.get("ai", {})
    personality_raw = raw.get("personality", {})

    feishu = FeishuConfig(
        app_id=_pick_str(feishu_raw, "app_id", ""),
        app_secret=_pick_str(feishu_raw, "app_secret", ""),
        webhook_url=_pick_str(feishu_raw, "webhook_url", ""),
    )
    ai = AIConfig(
        provider=_pick_str(ai_raw, "provider", "zhipu"),
        api_key=_pick_str(ai_raw, "api_key", ""),
        model=_pick_str(ai_raw, "model", "glm-4-flash"),
        base_url=_pick_str(ai_raw, "base_url", ""),
        timeout_seconds=_pick_int(ai_raw, "timeout_seconds", 30),
    )
    personality = PersonalityConfig(
        path=_pick_str(personality_raw, "path", "./crush-default/personality.md")
    )

    config = AppConfig(
        feishu=feishu,
        ai=ai,
        personality=personality,
        crush_name=_pick_str(raw, "crush_name", "小樱"),
        default_stage=_pick_str(raw, "default_stage", "陌生"),
        database_path=_pick_str(raw, "database_path", "./data/crush.db"),
        host=_pick_str(raw, "host", "0.0.0.0"),
        port=_pick_int(raw, "port", 5001),
        log_level=_pick_str(raw, "log_level", "INFO"),
    )
    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    missing = []
    if not config.feishu.app_id:
        missing.append("FEISHU_APP_ID")
    if not config.feishu.app_secret:
        missing.append("FEISHU_APP_SECRET")
    if not config.ai.api_key:
        missing.append("AI_API_KEY")

    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"缺少必要配置: {joined}")


def resolve_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (ROOT_DIR / path).resolve()
