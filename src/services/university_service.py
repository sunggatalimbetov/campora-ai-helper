from __future__ import annotations

import logging

from src.clients import supabase

logger = logging.getLogger(__name__)


def get_all_universities() -> list[tuple[str, str]]:
    """Return [(id, label), ...] for universities that have at least one chat mapping, ordered by id."""
    try:
        result = (
            supabase.table("universities")
            .select("id, label, university_chats(chat_id)")
            .order("id")
            .execute()
        )
        return [
            (row["id"], row["label"])
            for row in result.data
            if row.get("university_chats")
        ]
    except Exception as e:
        logger.error("Error fetching universities: %s", e)
        return []


def get_chat_ids_for_university(university_id: str) -> list[int]:
    """Return all chat_ids associated with the given university alias. Empty list if unknown."""
    try:
        result = (
            supabase.table("university_chats")
            .select("chat_id")
            .eq("university_id", university_id)
            .execute()
        )
        return [row["chat_id"] for row in result.data]
    except Exception as e:
        logger.error("Error fetching chat IDs for university '%s': %s", university_id, e)
        return []


def get_university_label(university_id: str) -> str:
    """Return the display label for the given university alias, or uppercased alias as fallback."""
    try:
        result = (
            supabase.table("universities")
            .select("label")
            .eq("id", university_id)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]["label"]
    except Exception as e:
        logger.error("Error fetching label for university '%s': %s", university_id, e)
    return university_id.upper()
