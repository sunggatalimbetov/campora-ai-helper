from typing import List, Tuple

from src.models.message import MessageDict
from src.services.message_search._clients import supabase
from src.services.message_search.get_embedding import get_embedding


def search_messages_semantic_only(query: str, count: int = 5) -> Tuple[List[MessageDict], List[float]]:
    """Fallback to pure semantic (vector) search."""
    query_embedding = get_embedding(query)

    try:
        resp = supabase.rpc("match_messages", {"query_embedding": query_embedding, "match_count": count}).execute()
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

    enhanced_results: List[MessageDict] = []
    for msg in messages:
        enhanced_results.append(msg)
        try:
            replies_response = supabase.table("messages").select("*").eq("reply_to_message_id", msg["id"]).eq("chat_id", msg["chat_id"]).execute()
            replies = replies_response.data
            if replies:
                for reply in replies:
                    enhanced_reply: MessageDict = {
                        **reply,
                        "is_reply": True,
                        "replying_to": msg["id"],
                        "similarity": msg.get("similarity", 0),
                    }
                    enhanced_results.append(enhanced_reply)
        except Exception as e:
            print(f"Error fetching replies for message {msg['id']}: {e}")

    return enhanced_results, query_embedding
