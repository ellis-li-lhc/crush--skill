from __future__ import annotations

from dataclasses import dataclass


STAGE_ORDER = ["陌生", "认识", "暧昧", "表白", "恋爱", "磨合", "长期"]

STAGE_THRESHOLDS = {
    "陌生": 0,
    "认识": 15,
    "暧昧": 35,
    "表白": 55,
    "恋爱": 75,
    "磨合": 95,
    "长期": 120,
}

POSITIVE_HINTS = [
    "喜欢",
    "想你",
    "爱你",
    "抱抱",
    "晚安",
    "早安",
    "陪我",
    "亲亲",
    "想见你",
    "开心",
]

NEGATIVE_HINTS = [
    "烦",
    "滚",
    "讨厌",
    "生气",
    "分手",
    "别烦我",
    "不想聊",
    "难过",
]


STAGE_RESPONSE_GUIDANCE = {
    "陌生": "保持礼貌和边界感，多接住对方话题，少用亲密称呼。",
    "认识": "可以主动记住小细节，回应更自然，但亲密度仍要克制。",
    "暧昧": "允许轻微试探、关心升级和一点点吃醋，但避免直接确认恋爱关系。",
    "表白": "回应可以更真诚明确，适合表达心动、确认感受和期待下一步。",
    "恋爱": "可以自然使用亲密称呼，增加陪伴感、报备感和稳定的情绪支持。",
    "磨合": "优先安抚情绪，再解释分歧，避免冷嘲热讽升级冲突。",
    "长期": "强调稳定陪伴、共同习惯和对未来的小计划。",
}


STAGE_EVENT_NOTES = {
    "认识": "阶段事件：关系从陌生进入认识，可以开始记住用户偏好并偶尔主动关心。",
    "暧昧": "阶段事件：关系进入暧昧，可以增加轻微试探、心动暗示和更细的情绪回应。",
    "表白": "阶段事件：关系进入表白节点，回应要更真诚，适合确认在意和关系期待。",
    "恋爱": "阶段事件：关系进入恋爱期，可以稳定使用亲密互动，但仍保持健康边界。",
    "磨合": "阶段事件：关系进入磨合期，冲突时先安抚情绪，再温和沟通。",
    "长期": "阶段事件：关系进入长期相处，重点是稳定陪伴、共同习惯和安全感。",
}


@dataclass
class StageEvent:
    stage: str
    note: str
    response_guidance: str


@dataclass
class RelationshipUpdate:
    delta: int
    favorability: int
    stage: str
    stage_changed: bool
    stage_before: str
    stage_after: str
    reason: str
    stage_event: StageEvent | None = None


def normalize_stage(stage: str) -> str:
    return stage if stage in STAGE_ORDER else STAGE_ORDER[0]


def stage_index(stage: str) -> int:
    return STAGE_ORDER.index(normalize_stage(stage))


def resolve_stage_from_favorability(favorability: int, current_stage: str) -> str:
    favorability = max(0, favorability)
    resolved = STAGE_ORDER[0]
    for stage in STAGE_ORDER:
        if favorability >= STAGE_THRESHOLDS[stage]:
            resolved = stage

    current_index = stage_index(current_stage)
    resolved_index = stage_index(resolved)
    if resolved_index < current_index and current_stage != "磨合":
        return current_stage
    return resolved


def build_stage_guidance(stage: str) -> str:
    normalized = normalize_stage(stage)
    return STAGE_RESPONSE_GUIDANCE[normalized]


def build_stage_event(stage_before: str, stage_after: str) -> StageEvent | None:
    if stage_before == stage_after:
        return None
    note = STAGE_EVENT_NOTES.get(stage_after)
    if not note:
        return None
    return StageEvent(
        stage=stage_after,
        note=note,
        response_guidance=build_stage_guidance(stage_after),
    )


def analyze_message_delta(message: str) -> tuple[int, str]:
    text = message.strip()
    if not text:
        return 0, "空消息"

    delta = 1
    reasons = ["完成一次对话"]

    if len(text) >= 12:
        delta += 1
        reasons.append("内容更认真")

    positive_hits = sum(1 for keyword in POSITIVE_HINTS if keyword in text)
    negative_hits = sum(1 for keyword in NEGATIVE_HINTS if keyword in text)

    if positive_hits:
        delta += min(positive_hits * 2, 6)
        reasons.append("表达了更多好感")

    if negative_hits:
        delta -= min(negative_hits * 2, 6)
        reasons.append("情绪有些低落或冲突")

    if any(word in text for word in ["谢谢", "辛苦", "晚安", "早安"]):
        delta += 1
        reasons.append("互动很礼貌温柔")

    delta = max(-4, min(delta, 8))
    return delta, "，".join(reasons)


def apply_relationship_progress(
    current_stage: str,
    current_favorability: int,
    user_message: str,
) -> RelationshipUpdate:
    stage_before = normalize_stage(current_stage)
    delta, reason = analyze_message_delta(user_message)
    favorability = max(0, current_favorability + delta)
    stage_after = resolve_stage_from_favorability(favorability, stage_before)
    stage_event = build_stage_event(stage_before, stage_after)

    return RelationshipUpdate(
        delta=delta,
        favorability=favorability,
        stage=stage_after,
        stage_changed=stage_after != stage_before,
        stage_before=stage_before,
        stage_after=stage_after,
        reason=reason,
        stage_event=stage_event,
    )


def build_status_text(stage: str, favorability: int, turns: int) -> str:
    return (
        f"当前关系阶段：{normalize_stage(stage)}\n"
        f"当前好感度：{favorability}\n"
        f"累计对话轮数：{turns}\n"
        "可用命令：/crush-status, /crush-set-stage 阶段名"
    )
