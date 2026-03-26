from typing import List

from src.config.settings import HYBRID_SEARCH_ENABLED, MIN_RESULT_SCORE
from src.models.message import MessageDict
from src.services.message_search.get_search_weights import get_search_weights
from src.services.message_search.reply_fetching import fetch_replies_by_parent
from src.services.message_search.search_messages_by_questions import (
    search_messages_by_questions,
)
from src.services.message_search.search_messages_hybrid import search_messages_hybrid
from src.services.message_search.search_messages_semantic_only import (
    search_messages_semantic_only,
)


def _merge_results(
    hybrid_results: List[MessageDict],
    question_results: List[MessageDict],
) -> List[MessageDict]:
    """
    Merge hybrid search results with question-based results.

    Deduplicates by message ID (excluding reply entries), keeping
    the entry with the higher similarity score. Reply entries from
    hybrid results are preserved as-is.
    """
    # Collect all reply entries from hybrid results unchanged
    replies = [r for r in hybrid_results if r.get("is_reply", False)]

    # Build a map of non-reply entries by (id, chat_id) to handle cross-chat duplicates
    by_key: dict[tuple[int, int], MessageDict] = {}
    for r in hybrid_results:
        if r.get("is_reply", False):
            continue
        key = (r["id"], r["chat_id"])
        if key not in by_key or r.get("similarity", 0) > by_key[key].get("similarity", 0):
            by_key[key] = r

    # Merge question results — add new messages or upgrade similarity
    new_from_questions = 0
    for r in question_results:
        key = (r["id"], r["chat_id"])
        if key not in by_key:
            by_key[key] = r
            new_from_questions += 1
        elif r.get("similarity", 0) > by_key[key].get("similarity", 0):
            # Keep the higher similarity, note the source
            by_key[key]["similarity"] = r["similarity"]
            by_key[key]["match_source"] = r.get("match_source", "question")

    if new_from_questions:
        print(f"🔀 Merged: {new_from_questions} new messages from question search")

    # Sort non-reply messages by similarity descending
    merged = sorted(by_key.values(), key=lambda x: x.get("similarity", 0), reverse=True)

    # Fetch replies for merged messages that do not already have them.
    existing_reply_parents = {(r.get("replying_to"), r.get("chat_id")) for r in replies}
    missing_reply_parents = [msg for msg in merged if (msg["id"], msg["chat_id"]) not in existing_reply_parents]
    replies_by_parent = fetch_replies_by_parent(missing_reply_parents)

    for msg in missing_reply_parents:
        for reply in replies_by_parent.get((msg["id"], msg["chat_id"]), []):
            enhanced_reply: MessageDict = {
                **reply,
                "is_reply": True,
                "replying_to": msg["id"],
                "similarity": msg.get("similarity", 0),
            }
            replies.append(enhanced_reply)

    return merged + replies


def search_messages(query: str, count: int = 5) -> tuple[List[MessageDict], List[float]]:
    """
    Search for messages using hybrid search (vector + full-text) with dynamic weights,
    then merge with question-embedding search for improved retrieval.

    Falls back to pure semantic search if hybrid_search RPC is unavailable.
    """
    if HYBRID_SEARCH_ENABLED:
        semantic_weight, full_text_weight = get_search_weights(query)
        results, query_embedding = search_messages_hybrid(
            query=query,
            count=count,
            semantic_weight=semantic_weight,
            full_text_weight=full_text_weight,
        )
    else:
        results, query_embedding = search_messages_semantic_only(query, count)

    # Also search via hypothetical question embeddings
    print("🔍 Searching message_questions...")
    question_results = search_messages_by_questions(query_embedding, count=count)

    # Merge hybrid + question results
    if question_results:
        results = _merge_results(results, question_results)

    filtered_results = [r for r in results if r.get("similarity", 0) >= MIN_RESULT_SCORE]

    top_results = [r for r in filtered_results if not r.get("is_reply", False)]
    print(f"📊 Found {len(top_results)} top results after filtering (score >= {MIN_RESULT_SCORE})")

    return filtered_results, query_embedding
