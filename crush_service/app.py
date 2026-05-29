from __future__ import annotations

import json
import logging
from pathlib import Path

from flask import Flask, jsonify, request

from crush_service.ai_client import AIClient
from crush_service.commands import maybe_handle_command
from crush_service.config import AppConfig, resolve_path
from crush_service.feishu_client import FeishuClient
from crush_service.persona import load_persona
from crush_service.prompting import ConversationContext, build_messages
from crush_service.relationship import apply_relationship_progress
from crush_service.state_store import StateStore


LOGGER = logging.getLogger(__name__)


def create_app(config: AppConfig) -> Flask:
    app = Flask(__name__)
    feishu_client = FeishuClient(config.feishu)
    ai_client = AIClient(config.ai)
    state_store = StateStore(
        database_path=resolve_path(config.database_path),
        default_stage=config.default_stage,
        default_persona_path=config.personality.path,
    )
    processed_events: set[str] = set()

    @app.route("/webhook", methods=["GET", "POST"])
    def handle_webhook():
        if request.method == "GET":
            challenge = request.args.get("challenge")
            if challenge:
                return jsonify({"code": 0, "challenge": challenge})
            return jsonify({"code": 1})

        payload = request.get_json(silent=True) or {}
        header = payload.get("header", {})
        event_id = header.get("event_id")
        if event_id and event_id in processed_events:
            LOGGER.info("Skip duplicate event: %s", event_id)
            return jsonify({"code": 0})
        if event_id:
            processed_events.add(event_id)
            if len(processed_events) > 1000:
                processed_events.clear()

        event = payload.get("event", {}) or payload
        message = event.get("message", {}) or event
        msg_type = message.get("message_type") or message.get("type")
        if msg_type != "text":
            LOGGER.info("Ignore non-text message type: %s", msg_type)
            return jsonify({"code": 0})

        content = _parse_message_content(message.get("content", "{}"))
        user_message = content.get("text", "").strip()
        sender = event.get("sender", {})
        sender_id = sender.get("sender_id", {})
        user_id = sender_id.get("open_id", "")

        if not user_message or not user_id:
            LOGGER.warning("Missing user_message or user_id in event: %s", payload)
            return jsonify({"code": 0})

        LOGGER.info("Received message from %s: %s", user_id, user_message)
        state = state_store.get_or_create_user_state(user_id)
        command_result = maybe_handle_command(user_message, user_id, state, state_store)
        if command_result.handled:
            try:
                token = feishu_client.get_token()
                feishu_client.send_text_message(token, user_id, command_result.reply)
            except Exception as exc:
                LOGGER.exception("Failed to send command reply: %s", exc)
            return jsonify({"code": 0})

        relationship_update = apply_relationship_progress(
            current_stage=state.stage,
            current_favorability=state.favorability,
            user_message=user_message,
        )
        persona = load_persona(
            config,
            custom_path=state.persona_path,
            stage=relationship_update.stage,
            custom_name=state.persona_name or None,
        )
        context = ConversationContext(
            user_id=user_id,
            stage=relationship_update.stage,
            favorability=relationship_update.favorability,
            conversation_turns=state.conversation_turns + 1,
            recent_messages=state.recent_messages,
            memory_notes=state.memory_notes,
        )

        try:
            messages = build_messages(persona, context, user_message)
            reply = ai_client.generate_reply(messages)
            updated_state = state_store.save_conversation_turn(
                user_id,
                user_message,
                reply,
                favorability=relationship_update.favorability,
                stage=relationship_update.stage,
                relationship_note=(
                    f"关系阶段变化：{relationship_update.stage_before} -> {relationship_update.stage_after}"
                    if relationship_update.stage_changed
                    else None
                ),
            )
            LOGGER.info(
                "Generated reply for %s at stage %s (favorability=%s delta=%s)",
                user_id,
                updated_state.stage,
                updated_state.favorability,
                relationship_update.delta,
            )
        except Exception as exc:
            LOGGER.exception("Failed to generate reply: %s", exc)
            reply = "我刚刚有点走神了，再和我说一次吧。"

        try:
            token = feishu_client.get_token()
            feishu_client.send_text_message(token, user_id, reply)
        except Exception as exc:
            LOGGER.exception("Failed to send Feishu reply: %s", exc)

        return jsonify({"code": 0})

    @app.route("/health", methods=["GET"])
    def health():
        db_path = Path(resolve_path(config.database_path))
        return jsonify(
            {
                "status": "ok",
                "database_path": str(db_path),
                "persona_path": str(resolve_path(config.personality.path)),
            }
        )

    return app


def _parse_message_content(content: str | dict) -> dict:
    if isinstance(content, dict):
        return content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"text": str(content)}
