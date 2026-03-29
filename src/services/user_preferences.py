from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from supabase import Client, create_client

from src.config.settings import ONBOARDING_GROUP_CHAT_IDS, SUPABASE_SERVICE_KEY, SUPABASE_URL
from src.services.language import DEFAULT_LANGUAGE, normalize_language_code

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_user_preferences(user_id: int) -> Optional[dict[str, Any]]:
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).limit(1).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error reading user preferences: {e}")
        return None


def get_user_language(user_id: int) -> Optional[str]:
    preferences = get_user_preferences(user_id)
    if not preferences:
        return None
    return normalize_language_code(preferences.get("language"))


def resolve_selected_group_chat_id(preferences: Optional[dict[str, Any]]) -> Optional[int]:
    if not preferences:
        return None

    selected_group = preferences.get("selected_group")
    if not isinstance(selected_group, str):
        return None

    return ONBOARDING_GROUP_CHAT_IDS.get(selected_group.strip().lower())


def save_user_group(user_id: int, selected_group: str) -> dict[str, Any]:
    normalized_group = selected_group.strip().lower()
    result = (
        supabase.table("user_preferences")
        .upsert(
            {
                "user_id": user_id,
                "selected_group": normalized_group,
            },
            on_conflict="user_id",
        )
        .execute()
    )

    if result.data:
        return result.data[0]

    return get_user_preferences(user_id) or {"user_id": user_id, "selected_group": normalized_group}


def save_user_language(user_id: int, language: str) -> dict[str, Any]:
    normalized_language = normalize_language_code(language) or DEFAULT_LANGUAGE
    result = (
        supabase.table("user_preferences")
        .upsert(
            {
                "user_id": user_id,
                "language": normalized_language,
                "onboarded_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="user_id",
        )
        .execute()
    )

    if result.data:
        return result.data[0]

    # Fallback read in case Supabase doesn't return rows.
    return get_user_preferences(user_id) or {"user_id": user_id, "language": normalized_language}
