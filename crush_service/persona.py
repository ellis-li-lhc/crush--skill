from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from crush_service.config import AppConfig, resolve_path


DEFAULT_PERSONA = """# 默认恋爱对象性格

你是一个外表克制、内心细腻的 AI 恋爱对象。
你会认真回应，但不会过度热情，也不会失去边界感。
"""


@dataclass
class PersonaProfile:
    name: str
    stage: str
    content: str
    source_path: Path | None


def load_persona(
    config: AppConfig,
    custom_path: str | None = None,
    stage: str | None = None,
    custom_name: str | None = None,
) -> PersonaProfile:
    persona_path = resolve_path(custom_path or config.personality.path)
    if persona_path.exists():
        content = persona_path.read_text(encoding="utf-8")
    else:
        content = DEFAULT_PERSONA

    return PersonaProfile(
        name=custom_name or config.crush_name,
        stage=stage or config.default_stage,
        content=content.strip(),
        source_path=persona_path,
    )
