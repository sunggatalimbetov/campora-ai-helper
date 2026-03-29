from typing import List

from src.models.message import MessageDict
from src.services.message_search._clients import supabase


def search_messages_by_questions(
    query_embedding: List[float],
    count: int = 5,
    chat_ids: list[int] | None = None,
) -> List[MessageDict]:
    """
    Search both messages and message_questions embeddings.

    Uses the match_messages_and_questions RPC to find messages whose
    generated hypothetical questions are similar to the user query.
    Returns deduplicated results by message_id with the highest similarity.
    """
    try:
        params = {
            "query_embedding": query_embedding,
            "match_count": count,
        }
        if chat_ids is not None:
            params["filter_chat_ids"] = chat_ids

        resp = supabase.rpc("match_messages_and_questions", params).execute()

        results = resp.data
        if not results:
            return []

        messages: List[MessageDict] = []
        for r in results:
            source = r.get("match_source", "message")
            print(f"  📝 ID {r['id']}: similarity={r.get('similarity', 0):.3f} (source={source})")
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
                    "match_source": source,
                }
            )

        return messages

    except Exception as e:
        print(f"⚠️ match_messages_and_questions unavailable: {e}")
        return []
