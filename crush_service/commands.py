from __future__ import annotations

from dataclasses import dataclass

from crush_service.persona_builder import (
    CREATOR_STEPS,
    STEP_PROMPTS,
    answer_creator,
    build_summary,
    current_step,
    save_persona_for_user,
    start_creator,
)
from crush_service.relationship import STAGE_ORDER, build_status_text, normalize_stage
from crush_service.state_store import StateStore, UserState


@dataclass
class CommandResult:
    handled: bool
    reply: str = ""


def maybe_handle_command(message: str, user_id: str, state: UserState, state_store: StateStore) -> CommandResult:
    text = message.strip()
    if state.creator_state and not text.startswith("/"):
        next_state, reply, _ = answer_creator(state.creator_state, text)
        state_store.update_creator_state(user_id, next_state)
        return CommandResult(handled=True, reply=reply)

    if not text.startswith("/"):
        return CommandResult(handled=False)

    if text == "/crush":
        creator_state = start_creator()
        state_store.update_creator_state(user_id, creator_state)
        first_step = current_step(creator_state)
        return CommandResult(
            handled=True,
            reply=(
                "我们来创建你的专属恋爱对象。\n"
                "接下来我会一步步问你，随时可以用 `/crush cancel` 取消。\n"
                f"{STEP_PROMPTS[first_step]}"
            ),
        )

    if text == "/crush cancel":
        state_store.update_creator_state(user_id, None)
        return CommandResult(handled=True, reply="这次创建先帮你取消了。想继续时再发 `/crush`。")

    if text == "/crush preview":
        if not state.creator_state or not state.creator_state.get("profile"):
            return CommandResult(handled=True, reply="你还没有进行中的创建流程，先发 `/crush` 开始。")
        return CommandResult(handled=True, reply=build_summary(state.creator_state["profile"]))

    if text == "/crush confirm":
        if not state.creator_state:
            return CommandResult(handled=True, reply="你还没有进行中的创建流程，先发 `/crush` 开始。")
        if state.creator_state.get("step_index", 0) < len(CREATOR_STEPS):
            return CommandResult(
                handled=True,
                reply=f"还没收集完，先回答这个问题：{STEP_PROMPTS[current_step(state.creator_state)]}",
            )

        profile = state.creator_state["profile"]
        persona_path, persona_name = save_persona_for_user(user_id, profile)
        updated = state_store.update_persona_binding(user_id, persona_name, persona_path, profile["stage"])
        return CommandResult(
            handled=True,
            reply=(
                f"已经创建好你的专属角色：{updated.persona_name}\n"
                f"人格文件：{updated.persona_path}\n"
                f"当前阶段：{updated.stage}\n"
                "现在直接和 Ta 聊天就可以了，或者发 `/crush-status` 看状态。"
            ),
        )

    if text == "/crush-status":
        return CommandResult(
            handled=True,
            reply=build_status_text(state.stage, state.favorability, state.conversation_turns),
        )

    if text == "/crush-persona":
        return CommandResult(
            handled=True,
            reply=(
                f"当前角色：{state.persona_name or '默认角色'}\n"
                f"人格文件：{state.persona_path}\n"
                f"当前阶段：{state.stage}\n"
                f"当前好感度：{state.favorability}"
            ),
        )

    if text.startswith("/crush-set-stage"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            return CommandResult(
                handled=True,
                reply=f"请在命令后面加阶段名，例如：/crush-set-stage 暧昧。可选阶段：{' / '.join(STAGE_ORDER)}",
            )

        target_stage = normalize_stage(parts[1].strip())
        if parts[1].strip() not in STAGE_ORDER:
            return CommandResult(
                handled=True,
                reply=f"未识别的阶段：{parts[1].strip()}。可选阶段：{' / '.join(STAGE_ORDER)}",
            )

        updated = state_store.update_stage(user_id, target_stage)
        return CommandResult(
            handled=True,
            reply=f"已经把当前关系阶段调整为：{updated.stage}\n当前好感度：{updated.favorability}",
        )

    return CommandResult(handled=False)
