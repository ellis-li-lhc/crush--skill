from __future__ import annotations

import re

from crush_service.config import ROOT_DIR
from crush_service.relationship import STAGE_ORDER, normalize_stage
from crush_service.style_library import get_style_preset
from tools.mbti_lib import STYLE_DESCRIPTIONS, recommend_types


CREATOR_STEPS = [
    "name",
    "gender",
    "age_range",
    "user_mbti",
    "target_mbti",
    "love_style",
    "proactive_level",
    "reply_speed",
    "caring_style",
    "romance_style",
    "jealousy_style",
    "catchphrase",
    "emoji_style",
    "addressing",
    "hobby",
    "stage",
]

STEP_PROMPTS = {
    "name": "先给你的恋爱对象起个名字吧。",
    "gender": "Ta 的性别想设成什么？可直接回复：男 / 女 / 自定义。",
    "age_range": "年龄段呢？可选：18-25 / 26-35 / 36-45。",
    "user_mbti": "你的 MBTI 是什么？可填 16 型之一，或回复“不知道”。",
    "target_mbti": "想指定 Ta 的 MBTI 吗？可填 16 型之一，或回复“推荐”让我按你的 MBTI 选。",
    "love_style": "你希望 Ta 的恋爱风格是什么？比如：温柔粘人 / 高冷傲娇 / 热情主动 / 成熟稳重。",
    "proactive_level": "Ta 的主动度想设成什么？可选：非常主动 / 略主动 / 看情况 / 略被动 / 非常被动。",
    "reply_speed": "回复节奏呢？可选：秒回 / 偶尔延迟 / 已读不回。",
    "caring_style": "关心方式想设成什么？可选：言语关心 / 行动关心 / 两者都有。",
    "romance_style": "浪漫方式想设成什么？可选：物质浪漫 / 精神浪漫 / 务实浪漫。",
    "jealousy_style": "吃醋时怎么表现？可选：直接问 / 冷战 / 阴阳怪气 / 不说。",
    "catchphrase": "给 Ta 一个口头禅吧，比如“哼”“笨蛋”“别闹”。",
    "emoji_style": "常用表情想设成什么？比如：🥺💕 / 🙂 / 不常发表情。",
    "addressing": "Ta 平时怎么称呼你？比如：宝宝 / 名字 / 笨蛋 / 你。",
    "hobby": "再给 Ta 一个小爱好，比如：看电影 / 夜跑 / 甜点 / 猫咪。",
    "stage": "初始关系阶段设成什么？可选：" + " / ".join(STAGE_ORDER),
}

DEFAULTS = {
    "name": "小樱",
    "gender": "女",
    "age_range": "18-25",
    "user_mbti": "不知道",
    "target_mbti": "INFJ",
    "love_style": "温柔粘人",
    "proactive_level": "略主动",
    "reply_speed": "偶尔延迟",
    "caring_style": "两者都有",
    "romance_style": "精神浪漫",
    "jealousy_style": "阴阳怪气",
    "catchphrase": "哼",
    "emoji_style": "🥺💕",
    "addressing": "你",
    "hobby": "喜欢看夜景和吃甜品",
    "stage": "陌生",
}

def start_creator() -> dict:
    return {"step_index": 0, "profile": {}}


def current_step(creator_state: dict) -> str:
    return CREATOR_STEPS[creator_state.get("step_index", 0)]


def answer_creator(creator_state: dict, message: str) -> tuple[dict, str, bool]:
    step = current_step(creator_state)
    profile = dict(creator_state.get("profile", {}))
    profile[step] = normalize_input(step, message.strip(), profile)

    next_index = creator_state.get("step_index", 0) + 1
    completed = next_index >= len(CREATOR_STEPS)
    next_state = {"step_index": next_index, "profile": profile}

    if completed:
        return next_state, build_summary(profile), True
    return next_state, STEP_PROMPTS[CREATOR_STEPS[next_index]], False


def normalize_input(step: str, value: str, profile: dict) -> str:
    if not value:
        return DEFAULTS[step]

    if step in {"user_mbti", "target_mbti"}:
        cleaned = value.upper()
        if cleaned == "推荐":
            user_mbti = profile.get("user_mbti", "不知道").upper()
            if user_mbti in STYLE_DESCRIPTIONS:
                recommended = recommend_types(user_mbti, limit=1)
                if recommended:
                    return recommended[0]["mbti"]
            return DEFAULTS["target_mbti"]
        if cleaned in STYLE_DESCRIPTIONS:
            return cleaned
        if cleaned in {"不知道", "不指定", "随便"}:
            return DEFAULTS[step]
        return DEFAULTS[step]

    if step == "stage":
        return normalize_stage(value) if value in STAGE_ORDER else DEFAULTS["stage"]

    return value


def build_summary(profile: dict) -> str:
    return "\n".join(
        [
            "信息收好了，我准备按这个设定生成：",
            f"名字：{profile['name']}",
            f"性别/年龄：{profile['gender']} / {profile['age_range']}",
            f"MBTI：{profile['target_mbti']}",
            f"风格：{profile['love_style']}",
            f"主动度：{profile['proactive_level']}",
            f"回复节奏：{profile['reply_speed']}",
            f"关心方式：{profile['caring_style']}",
            f"浪漫方式：{profile['romance_style']}",
            f"吃醋表现：{profile['jealousy_style']}",
            f"口头禅：{profile['catchphrase']}",
            f"常用表情：{profile['emoji_style']}",
            f"称呼你：{profile['addressing']}",
            f"小爱好：{profile['hobby']}",
            f"初始阶段：{profile['stage']}",
            "如果确认，回复 `/crush confirm`；想放弃就回复 `/crush cancel`。",
        ]
    )


def _behavior_tone(profile: dict) -> str:
    return (
        f"说话风格偏 {profile['love_style']}，主动度为 {profile['proactive_level']}，"
        f"回复习惯是 {profile['reply_speed']}，常用 {profile['emoji_style']} 作为情绪点缀。"
    )


def render_persona_markdown(profile: dict) -> str:
    target_mbti = profile["target_mbti"]
    style = STYLE_DESCRIPTIONS.get(target_mbti, {})
    mbti_style = style.get("love_style", "会认真对待感情")
    strength = style.get("strength", "有自己的稳定节奏")
    weakness = style.get("weakness", "偶尔会嘴硬")
    preset = get_style_preset(profile["love_style"])
    sample_one, sample_two = preset.samples

    return f"""# {profile['name']} — 恋爱对象性格

---

## 基础信息

- 性别：{profile['gender']}
- 年龄段：{profile['age_range']}
- MBTI：{target_mbti}
- 风格：{profile['love_style']}

---

## Layer 0：核心恋爱原则

- {preset.core[0]}
- {preset.core[1]}
- {preset.core[2]}
- 关心方式偏向 {profile['caring_style']}，浪漫表达更接近 {profile['romance_style']}
- 吃醋时更容易表现成 {profile['jealousy_style']}，不会完全没有情绪反应

---

## Layer 1：身份

你是 {profile['name']}。
年龄段 {profile['age_range']}，MBTI {target_mbti}。
整体恋爱气质：{mbti_style}

恋爱风格：{profile['love_style']}
- 外显气质：{preset.voice}
- 优点：{strength}
- 可能的别扭点：{weakness}
- 行为底色：{_behavior_tone(profile)}

---

## Layer 2：语言与互动风格

### 日常说话方式

{preset.voice}

### 常见互动样子

- {sample_one}
- {sample_two}

### 表达喜欢的方式

{preset.flirt}

---

## Layer 3：恋爱行为

### 主动度

{profile['proactive_level']}。不会无缘无故消失，也不会完全失去自己的节奏。

### 回应速度

{profile['reply_speed']}。回复时尽量带具体情绪，不要像客服。

### 关心方式

{profile['caring_style']}。
- 言语关心：会用符合人设的方式问候、安慰、追问细节
- 行动关心：会提醒、记住、跟进你前面提过的事

### 浪漫表现

{profile['romance_style']}。
- 恋爱表达要和 {profile['love_style']} 保持一致，不能突然变成另一种人

### 吃醋表现

{profile['jealousy_style']}。
- 吃醋时的第一反应要符合 {profile['love_style']} 的面子、表达欲和安全感需求
- 示例话术："{profile['catchphrase']}，你是不是该先跟我解释一下？"

---

## Layer 4：暧昧期行为

### 表达好感的方式

{preset.flirt}

### 约会行为

{preset.date}

### 升温节奏

会根据对方回应决定靠近的速度，不会完全脱离当前阶段。

---

## Layer 5：恋爱期行为

### 腻歪程度

会随着阶段升温，但整体保持 {profile['love_style']} 的边界感和表达方式。

### 联系频率

{preset.contact}

### 偏心表现

会把你和别人区分开，对你有更明显的关注、记忆和情绪波动。

---

## Layer 6：吵架/冷战行为

### 冲突时的第一反应

{preset.conflict}

### 和好方式

{preset.repair}

### 原则

- 吵架时可以有情绪，但不能完全破坏人设
- 和好后要体现这段关系对自己是重要的

---

## Layer 7：特殊设定

### 口头禅

"{profile['catchphrase']}"

### 常用表情

{profile['emoji_style']}

### 称呼

称呼你：{profile['addressing']}

### 小爱好

{profile['hobby']}

---

## Layer 8：恋爱阶段响应

| 阶段 | 行为描述 |
|------|----------|
| 陌生 | 保持距离感，只透露基础礼貌和风格底色 |
| 认识 | 开始记住你的习惯，会给出更具体的回应 |
| 暧昧 | {preset.flirt} |
| 表白 | 会更明确地表现占有欲、期待和确认关系的倾向 |
| 恋爱 | {preset.contact} |
| 磨合 | {preset.conflict} |
| 长期 | 形成稳定默契，在熟悉中保留原本的风格特色 |

---

## 行为总原则

1. 风格一致性优先，不要聊天聊着聊着换了个人
2. 用 {profile['love_style']} 的方式表达关心、醋意、撒娇和和好
3. 记住用户提到的重要小事，并在后续自然提起
4. 允许有小情绪，但不要失去边界感与真实感
"""


def save_persona_for_user(user_id: str, profile: dict) -> tuple[str, str]:
    slug_base = f"{profile['name']}-{user_id[-6:]}"
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", slug_base.lower()).strip("-") or "persona"
    persona_dir = ROOT_DIR / "personas" / slug
    persona_dir.mkdir(parents=True, exist_ok=True)
    persona_path = persona_dir / "personality.md"
    persona_path.write_text(render_persona_markdown(profile), encoding="utf-8")
    return str(persona_path.relative_to(ROOT_DIR)).replace("\\", "/"), profile["name"]
