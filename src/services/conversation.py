import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set, Tuple

from src.clients import supabase
from src.config.settings import (
    CONVERSATION_MAX_TURNS,
    CONVERSATION_TIMEOUT_MINUTES,
)

logger = logging.getLogger(__name__)

_MAX_RESET_SESSIONS = 10_000
_reset_sessions: Set[Tuple[int, int]] = set()


@dataclass
class ConversationTurn:
    query: str
    answer: str
    timestamp: datetime


def load_conversation_history(user_id: int, chat_id: int) -> Tuple[List[ConversationTurn], Optional[str]]:
    """
    Load recent conversation turns from bot_interactions.

    Returns (turns, session_id) where session_id is the existing session's ID
    if continuing a conversation, or a fresh UUID if starting new.
    """
    if (user_id, chat_id) in _reset_sessions:
        _reset_sessions.discard((user_id, chat_id))
        return [], str(uuid.uuid4())

    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=CONVERSATION_TIMEOUT_MINUTES)).isoformat()

    try:
        result = (
            supabase.table("bot_interactions")
            .select("input_message, output_message, session_id, created_at")
            .eq("user_id", user_id)
            .eq("chat_id", chat_id)
            .eq("status", "success")
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .limit(CONVERSATION_MAX_TURNS)
            .execute()
        )
    except Exception as e:
        logger.error("Error loading conversation history: %s", e)
        return [], str(uuid.uuid4())

    if not result.data:
        return [], str(uuid.uuid4())

    rows = list(reversed(result.data))

    session_id = rows[-1].get("session_id") or str(uuid.uuid4())

    turns = [
        ConversationTurn(
            query=row["input_message"],
            answer=row["output_message"],
            timestamp=row["created_at"],
        )
        for row in rows
    ]

    return turns, session_id


def mark_new_session(user_id: int, chat_id: int) -> None:
    """Mark that the next query for this user+chat should start a fresh session."""
    if len(_reset_sessions) >= _MAX_RESET_SESSIONS:
        # Eviction order is arbitrary (set has no ordering), which is fine —
        # entries are consumed on next query so the set rarely grows large.
        for _ in range(len(_reset_sessions) // 4):
            _reset_sessions.pop()
    _reset_sessions.add((user_id, chat_id))
