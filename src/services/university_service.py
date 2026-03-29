from __future__ import annotations

from supabase import Client, create_client

from src.config.settings import SUPABASE_SERVICE_KEY, SUPABASE_URL

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_all_universities() -> list[tuple[str, str]]:
    """Return [(id, label), ...] from the universities table, ordered by id."""
    try:
        result = supabase.table("universities").select("id, label").order("id").execute()
        return [(row["id"], row["label"]) for row in result.data]
    except Exception as e:
        print(f"Error fetching universities: {e}")
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
        print(f"Error fetching chat IDs for university '{university_id}': {e}")
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
        print(f"Error fetching label for university '{university_id}': {e}")
    return university_id.upper()
