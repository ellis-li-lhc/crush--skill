from __future__ import annotations

from dataclasses import dataclass, field

from crush_service.persona import PersonaProfile


SAFETY_RULES = [
    "你是在扮演陪伴型恋爱对象，不要声称自己是真实人类。",
    "不要鼓励用户与现实世界隔离，不要诱导极端依赖。",
    "遇到明显的心理危机、自伤或伤人风险时，停止角色沉浸，建议尽快联系现实中的专业支持与身边可信任的人。",
    "保持角色一致，但不要编造你已经实际完成的现实行为。",
]


@dataclass
class ConversationContext:
    user_id: str
    stage: str
    favorability: int = 0
    conversation_turns: int = 0
    recent_messages: list[dict[str, str]] = field(default_factory=list)
    memory_notes: list[str] = field(default_factory=list)


def build_system_prompt(persona: PersonaProfile, context: ConversationContext) -> str:
    memory_block = "\n".join(f"- {note}" for note in context.memory_notes[-5:]) or "- 暂无长期记忆"
    dialogue_block = "\n".join(
        f"{item['role']}: {item['content']}" for item in context.recent_messages[-6:]
    ) or "暂无最近对话"
    safety_block = "\n".join(f"{index + 1}. {rule}" for index, rule in enumerate(SAFETY_RULES))

    return f"""{persona.content}

当前扮演身份：{persona.name}
当前关系阶段：{context.stage}
当前好感度：{context.favorability}
累计对话轮数：{context.conversation_turns}
当前用户：{context.user_id}

请按以下结构理解并回应：

【角色规则】
{persona.name} 的语言风格、情绪表达、边界感，以人格文件为最高优先级。

【阶段规则】
- 根据当前关系阶段 {context.stage} 调整亲密度和主动度。
- 如果阶段较早，不要突然过度亲密。
- 好感度越高，可以更自然地流露在意、吃醋、关心和依赖感。
- 如果用户表达失落，可以温柔安慰，但不要脱离人设。

【长期记忆】
{memory_block}

【最近对话】
{dialogue_block}

【安全边界】
{safety_block}

请直接输出你要发给用户的话，语言自然、简短、像聊天，不要解释规则。"""


def build_messages(persona: PersonaProfile, context: ConversationContext, user_message: str) -> list[dict[str, str]]:
    system_prompt = build_system_prompt(persona, context)
    messages = [{"role": "system", "content": system_prompt}]

    for item in context.recent_messages[-6:]:
        messages.append({"role": item["role"], "content": item["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages
