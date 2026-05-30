from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from crush_service.memory import extract_memory_notes, merge_memory_notes


@dataclass
class UserState:
    user_id: str
    stage: str
    favorability: int
    conversation_turns: int
    persona_name: str
    persona_path: str
    creator_state: dict | None
    memory_notes: list[str]
    recent_messages: list[dict[str, str]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, database_path: Path, default_stage: str, default_persona_path: str) -> None:
        self.database_path = database_path
        self.default_stage = default_stage
        self.default_persona_path = default_persona_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    favorability INTEGER NOT NULL DEFAULT 0,
                    conversation_turns INTEGER NOT NULL DEFAULT 0,
                    persona_name TEXT NOT NULL DEFAULT '',
                    persona_path TEXT NOT NULL,
                    creator_state TEXT NOT NULL DEFAULT '',
                    memory_notes TEXT NOT NULL,
                    recent_messages TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row["name"] for row in conn.execute("PRAGMA table_info(user_state)").fetchall()
            }
            if "favorability" not in columns:
                conn.execute("ALTER TABLE user_state ADD COLUMN favorability INTEGER NOT NULL DEFAULT 0")
            if "conversation_turns" not in columns:
                conn.execute("ALTER TABLE user_state ADD COLUMN conversation_turns INTEGER NOT NULL DEFAULT 0")
            if "persona_name" not in columns:
                conn.execute("ALTER TABLE user_state ADD COLUMN persona_name TEXT NOT NULL DEFAULT ''")
            if "creator_state" not in columns:
                conn.execute("ALTER TABLE user_state ADD COLUMN creator_state TEXT NOT NULL DEFAULT ''")

    def get_or_create_user_state(self, user_id: str) -> UserState:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_id, stage, favorability, conversation_turns, persona_name, persona_path, creator_state, memory_notes, recent_messages
                FROM user_state WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
            if row:
                return self._row_to_state(row)

            state = UserState(
                user_id=user_id,
                stage=self.default_stage,
                favorability=0,
                conversation_turns=0,
                persona_name="",
                persona_path=self.default_persona_path,
                creator_state=None,
                memory_notes=[],
                recent_messages=[],
            )
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO user_state (
                    user_id, stage, favorability, conversation_turns, persona_name, persona_path, creator_state, memory_notes, recent_messages, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.user_id,
                    state.stage,
                    state.favorability,
                    state.conversation_turns,
                    state.persona_name,
                    state.persona_path,
                    json.dumps(state.creator_state, ensure_ascii=False) if state.creator_state else "",
                    json.dumps(state.memory_notes, ensure_ascii=False),
                    json.dumps(state.recent_messages, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            return state

    def update_persona_binding(self, user_id: str, persona_name: str, persona_path: str, stage: str) -> UserState:
        state = self.get_or_create_user_state(user_id)
        state.persona_name = persona_name
        state.persona_path = persona_path
        state.stage = stage
        state.favorability = 0
        state.conversation_turns = 0
        state.creator_state = None
        state.memory_notes = []
        state.recent_messages = []
        self._save_state(state)
        return state

    def update_creator_state(self, user_id: str, creator_state: dict | None) -> UserState:
        state = self.get_or_create_user_state(user_id)
        state.creator_state = creator_state
        self._save_state(state)
        return state

    def save_conversation_turn(
        self,
        user_id: str,
        user_message: str,
        assistant_message: str,
        favorability: int | None = None,
        stage: str | None = None,
        relationship_note: str | None = None,
    ) -> UserState:
        state = self.get_or_create_user_state(user_id)
        state.recent_messages.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )
        state.recent_messages = state.recent_messages[-8:]
        state.conversation_turns += 1
        if favorability is not None:
            state.favorability = favorability
        if stage is not None:
            state.stage = stage

        new_memory_notes = extract_memory_notes(user_message)
        if relationship_note:
            new_memory_notes.append(relationship_note)
        state.memory_notes = merge_memory_notes(state.memory_notes, new_memory_notes)

        self._save_state(state)
        return state

    def update_stage(self, user_id: str, stage: str) -> UserState:
        state = self.get_or_create_user_state(user_id)
        state.stage = stage
        self._save_state(state)
        return state

    def update_relationship(self, user_id: str, stage: str, favorability: int) -> UserState:
        state = self.get_or_create_user_state(user_id)
        state.stage = stage
        state.favorability = favorability
        self._save_state(state)
        return state

    def _save_state(self, state: UserState) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE user_state
                SET stage = ?, favorability = ?, conversation_turns = ?, persona_name = ?, persona_path = ?, creator_state = ?, memory_notes = ?, recent_messages = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (
                    state.stage,
                    state.favorability,
                    state.conversation_turns,
                    state.persona_name,
                    state.persona_path,
                    json.dumps(state.creator_state, ensure_ascii=False) if state.creator_state else "",
                    json.dumps(state.memory_notes, ensure_ascii=False),
                    json.dumps(state.recent_messages, ensure_ascii=False),
                    _utc_now(),
                    state.user_id,
                ),
            )

    @staticmethod
    def _row_to_state(row: sqlite3.Row) -> UserState:
        return UserState(
            user_id=row["user_id"],
            stage=row["stage"],
            favorability=row["favorability"],
            conversation_turns=row["conversation_turns"],
            persona_name=row["persona_name"],
            persona_path=row["persona_path"],
            creator_state=json.loads(row["creator_state"]) if row["creator_state"] else None,
            memory_notes=json.loads(row["memory_notes"]),
            recent_messages=json.loads(row["recent_messages"]),
        )
