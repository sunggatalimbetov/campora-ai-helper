import asyncio
from typing import List, Optional, Tuple

from src.models.message import MessageDict
from src.services.conversation import ConversationTurn, load_conversation_history
from src.services.message_search import search_messages
from src.services.message_search.rewrite_query import rewrite_query


async def run_search_pipeline(
    query: str,
    user_id: int,
    chat_id: int,
    search_chat_ids: Optional[List[int]],
) -> Tuple[List[ConversationTurn], str, str, List[MessageDict], List[float]]:
    """Load conversation history, rewrite the query, and run search.

    Returns:
        (history, session_id, search_query, results, query_embedding)
    """
    history, session_id = await asyncio.to_thread(load_conversation_history, user_id, chat_id)
    search_query = await asyncio.to_thread(rewrite_query, query, history)
    results, query_embedding = await asyncio.to_thread(search_messages, search_query, chat_ids=search_chat_ids)
    return history, session_id, search_query, results, query_embedding


def extract_result_metadata(results: List[MessageDict]) -> Tuple[List[int], List[float]]:
    """Extract message IDs and similarity scores from search results."""
    referenced_message_ids = [msg.get("id") for msg in results if msg.get("id") is not None]
    similarity_scores = [msg.get("similarity") for msg in results if msg.get("similarity") is not None]
    return referenced_message_ids, similarity_scores
