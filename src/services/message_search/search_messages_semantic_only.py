from typing import List, Tuple

from src.models.message import MessageDict
from src.services.message_search._clients import supabase
from src.services.message_search.get_embedding import get_embedding
from src.services.message_search.reply_fetching import attach_replies_to_messages


def search_messages_semantic_only(
    query: str,
    count: int = 5,
    chat_id: int | None = None,
) -> Tuple[List[MessageDict], List[float]]:
    """Fallback to pure semantic (vector) search."""
    query_embedding = get_embedding(query)

    try:
        params = {"query_embedding": query_embedding, "match_count": count}
        if chat_id is not None:
            params["filter_chat_id"] = chat_id
        resp = supabase.rpc("match_messages", params).execute()
    except Exception as e:
        print(f"Error in semantic search: {e}")
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
