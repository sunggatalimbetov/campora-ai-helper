from typing import List, Tuple

from src.config.settings import RRF_K, SIMILARITY_THRESHOLD
from src.models.message import MessageDict
from src.services.message_search.answer_utils import filter_by_similarity
from src.services.message_search._clients import supabase
from src.services.message_search.extract_fulltext_terms import extract_fulltext_terms
from src.services.message_search.get_embedding import get_embedding
from src.services.message_search.reply_fetching import attach_replies_to_messages
from src.services.message_search.search_messages_semantic_only import (
    search_messages_semantic_only,
)


def search_messages_hybrid(
    query: str,
    count: int = 5,
    semantic_weight: float = 0.5,
    full_text_weight: float = 0.5,
    chat_id: int | None = None,
) -> Tuple[List[MessageDict], List[float]]:
    """
    Hybrid search combining vector similarity and full-text search via RRF.
    """
    query_embedding = get_embedding(query)
    fulltext_query = extract_fulltext_terms(query)
    print(f'🔤 Fulltext terms: "{fulltext_query}"')

    try:
        params = {
            "query_text": fulltext_query,
            "query_embedding": query_embedding,
            "match_count": count,
            "semantic_weight": semantic_weight,
            "full_text_weight": full_text_weight,
            "rrf_k": RRF_K,
        }
        if chat_id is not None:
            params["filter_chat_id"] = chat_id

        resp = supabase.rpc("hybrid_search", params).execute()

        results = resp.data

        for r in results:
            print(f"  ID {r['id']}: semantic={r.get('semantic_similarity', 0):.3f}, " f"fulltext={r.get('full_text_rank', 0):.3f}, combined={r.get('combined_score', 0):.3f}")

        pre_filter_count = len(results)
        results = filter_by_similarity(results, SIMILARITY_THRESHOLD)
        if len(results) < pre_filter_count:
            print(f"🔻 Similarity filter ({SIMILARITY_THRESHOLD}): {pre_filter_count} → {len(results)} results")

        messages: List[MessageDict] = []
        for r in results:
            messages.append(
                {
                    "id": r["id"],
                    "chat_id": r["chat_id"],
                    "author": r["author"],
                    "text": r["text"],
                    "link": r["link"],
                    "reply_to_message_id": r["reply_to_message_id"],
                    "created_at": r.get("created_at"),
                    "similarity": r.get("semantic_similarity", 0),
                    "semantic_similarity": r.get("semantic_similarity"),
                    "full_text_rank": r.get("full_text_rank"),
                    "combined_score": r.get("combined_score"),
                }
            )

        return attach_replies_to_messages(messages), query_embedding

    except Exception as e:
        print(f"Error in hybrid search: {e}, falling back to semantic-only")
        return search_messages_semantic_only(query, count, chat_id=chat_id)
