import logging
from typing import List

from src.services.conversation import ConversationTurn
from src.services.message_search._clients import client_oa

logger = logging.getLogger(__name__)


def rewrite_query(query: str, history: List[ConversationTurn]) -> str:
    """
    Rewrite an ambiguous follow-up query into a standalone search query
    using the conversation history for context.

    Returns the original query unchanged when there is no history.
    """
    if not history:
        return query

    conversation_block = "\n".join(
        f"User: {turn.query}\nAssistant: {turn.answer}" for turn in history[-3:]
    )

    prompt = (
        "You are a query rewriter. Given a conversation history and the user's latest message, "
        "rewrite the latest message as a single standalone search query that captures the full intent. "
        "If the latest message is already self-contained, return it as-is. "
        "Do NOT answer the question — only output the rewritten query. "
        "Preserve the original language of the user's message."
    )

    try:
        response = client_oa.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=150,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"Conversation so far:\n{conversation_block}\n\nLatest message:\n{query}",
                },
            ],
        )
        rewritten = response.choices[0].message.content.strip()
        return rewritten or query
    except Exception as e:
        logger.error("Error rewriting query: %s", e)
        return query
