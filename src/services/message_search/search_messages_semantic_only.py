import logging
from typing import List, Tuple

from src.models.message import MessageDict
from src.services.message_search._clients import supabase

logger = logging.getLogger(__name__)
from src.services.message_search.get_embedding import get_embedding
from src.services.message_search.reply_fetching import attach_replies_to_messages


def search_messages_semantic_only(
    query: str,
    count: int = 5,
    chat_ids: list[int] | None = None,
) -> Tuple[List[MessageDict], List[float]]:
    """Fallback to pure semantic (vector) search."""
    query_embedding = get_embedding(query)

    try:
        params = {"query_embedding": query_embedding, "match_count": count}
        if chat_ids is not None:
            params["filter_chat_ids"] = chat_ids
        resp = supabase.rpc("match_messages", params).execute()
    except Exception as e:
        logger.error("Error in semantic search: %s", e)
        return [], query_embedding

    messages: List[MessageDict] = []
    for r in resp.data:
        messages.append(
            {
                "id": r["id"],
                "chat_id": r["chat_id"],
                "author": r["author"],
                "text": r["text"],
                "link": r["link"],
                "reply_to_message_id": r["reply_to_message_id"],
                "created_at": r.get("created_at"),
                "similarity": r.get("similarity", 0),
            }
        )

    return attach_replies_to_messages(messages), query_embedding
