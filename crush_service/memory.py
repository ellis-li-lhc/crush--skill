from __future__ import annotations

import re


MAX_MEMORY_NOTES = 14


def extract_memory_notes(message: str) -> list[str]:
    text = _compact(message)
    if not text:
        return []

    notes: list[str] = []
    notes.extend(_extract_named_preferences(text))
    notes.extend(_extract_simple_patterns(text))
    notes.extend(_extract_schedule(text))
    notes.extend(_extract_mood(text))

    if not notes:
        notes.append(f"最近话题：{_clip(text, 60)}")

    return _dedupe(notes)


def merge_memory_notes(existing: list[str], incoming: list[str], limit: int = MAX_MEMORY_NOTES) -> list[str]:
    merged: list[str] = []
    for note in [*existing, *incoming]:
        clean = _compact(note)
        if clean and clean not in merged:
            merged.append(clean)
    return merged[-limit:]


def _extract_named_preferences(text: str) -> list[str]:
    notes: list[str] = []
    for verb, label in [
        ("喜欢", "偏好"),
        ("爱吃", "饮食偏好"),
        ("想去", "想去的地方"),
        ("想看", "想看的内容"),
        ("想要", "愿望"),
    ]:
        for match in re.finditer(rf"我{verb}([^，。！？\n]{{1,28}})", text):
            value = _clean_value(match.group(1))
            if value:
                notes.append(f"{label}：用户{verb}{value}")
    return notes


def _extract_simple_patterns(text: str) -> list[str]:
    notes: list[str] = []
    for pattern, label, prefix in [
        (r"(?:我叫|叫我)([^，。！？\n]{1,12})", "称呼", "用户希望被称呼为"),
        (r"我(?:不喜欢|讨厌|害怕)([^，。！？\n]{1,28})", "边界", "用户不喜欢/在意"),
        (r"别(?:再)?([^，。！？\n]{1,24})", "边界", "用户明确提出不要"),
    ]:
        for match in re.finditer(pattern, text):
            value = _clean_value(match.group(1))
            if value:
                notes.append(f"{label}：{prefix}{value}")
    return notes


def _extract_schedule(text: str) -> list[str]:
    schedule_words = ["今天", "今晚", "明天", "后天", "周末", "下周", "考试", "面试", "加班", "出差", "约会"]
    if any(word in text for word in schedule_words):
        return [f"近期安排：{_clip(text, 70)}"]
    return []


def _extract_mood(text: str) -> list[str]:
    mood_words = ["开心", "难过", "累", "烦", "焦虑", "生气", "委屈", "失眠", "压力", "崩溃"]
    if any(word in text for word in mood_words):
        return [f"情绪线索：{_clip(text, 70)}"]
    return []


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clean_value(value: str) -> str:
    value = _compact(value)
    value = re.sub(r"^(吃|去|看|要|的是|这个|那个)", "", value)
    return _clip(value, 28)


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit] + "..."


def _dedupe(notes: list[str]) -> list[str]:
    result: list[str] = []
    for note in notes:
        if note and note not in result:
            result.append(note)
    return result
