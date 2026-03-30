from typing import AsyncGenerator, List, Optional

from src.services.conversation import ConversationTurn
from src.services.message_search._clients import async_client_oa
from src.services.message_search.generate_answer import build_messages


async def stream_answer(
    query: str,
    results: list,
    conversation_history: Optional[List[ConversationTurn]] = None,
    answer_language: str = "ru",
    chat_type: str = "private",
) -> AsyncGenerator[tuple[str | None, int | None], None]:
    """Stream an OpenAI answer, yielding text deltas and finally the token count.

    Yields:
        (delta_text, None) for each content chunk
        (None, total_tokens) on the final chunk with usage info
    """
    messages, question_results = build_messages(query, results, conversation_history, answer_language, chat_type)

    stream = await async_client_oa.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
        stream_options={"include_usage": True},
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield (chunk.choices[0].delta.content, None)
        if chunk.usage:
            yield (None, chunk.usage.total_tokens)
