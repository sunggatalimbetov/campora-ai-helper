from typing import List, Optional

from src.models.message import MessageDict
from src.services.conversation import ConversationTurn
from src.services.message_search._clients import client_oa

SYSTEM_PROMPT = """\
You are a helpful assistant for university students.
Your purpose is to answer questions related to university life: academics, exams, deadlines,
schedules, enrollment, bureaucracy, student services, housing, stress management, campus life,
and similar topics that students commonly face.

IMPORTANT — Topic filter:
First, determine whether the user's question is related to university or student life.
If the question is clearly off-topic (e.g. dating advice, cooking recipes, entertainment
recommendations, personal relationship tips, politics unrelated to university, etc.),
politely decline by saying something like: "I can only help with university-related questions.
Try asking me about exams, deadlines, enrollment, or anything else related to student life!"
Write the decline message in the same language as the user's question.
Do NOT attempt to answer off-topic questions even if the provided information seems loosely related.

If the question IS relevant to university/student life, answer it using ONLY the information
below, but do NOT mention that you are using any "context", "provided information",
or "sources" in your answer. Respond naturally and directly, as if you already know the answer.

The information includes both original relevant messages and their replies/answers.
Pay special attention to the replies as they often contain the actual answers to questions.

Note: Each message has a similarity score indicating how relevant it is to the query.
Higher scores (closer to 1.0) are more relevant.

Instructions:
- Answer directly and naturally — never say things like "based on the provided context",
  "в предоставленном контексте", "на основании предоставленного контекста",
  "according to the information I have", or similar phrases
- Prioritize information from replies/answers when available
- Consider similarity scores when weighing the importance of information
- Newer messages are generally more reliable, especially for time-sensitive topics like
  admission requirements, deadlines, or procedures. If older and newer messages conflict,
  prefer the newer one.
- Write your response in the same language as the user's question
- Do NOT include any links in your answer - they will be added automatically"""


def _build_context(results: list) -> tuple[str, List[MessageDict], List[MessageDict]]:
    question_results: List[MessageDict] = [msg for msg in results if not msg.get("is_reply", False)]
    reply_results: List[MessageDict] = [msg for msg in results if msg.get("is_reply", False)]

    context_parts: List[str] = []

    if question_results:
        context_parts.append("Original relevant messages:")
        for i, msg in enumerate(question_results):
            similarity = msg.get("similarity", 0)
            date_str = msg.get("created_at", "")
            date_label = f" [Date: {date_str[:10]}]" if date_str else ""
            context_parts.append(f"{i+1}. (Similarity: {similarity:.2f}){date_label} {msg['text']}")

    if reply_results:
        context_parts.append("\nReplies/Answers to these messages:")
        for i, msg in enumerate(reply_results):
            similarity = msg.get("similarity", 0)
            date_str = msg.get("created_at", "")
            date_label = f" [Date: {date_str[:10]}]" if date_str else ""
            context_parts.append(f"Reply {i+1}. (Similarity: {similarity:.2f}){date_label} {msg['text']}")

    return "\n".join(context_parts), question_results, reply_results


def generate_answer(
    query: str,
    results: list,
    conversation_history: Optional[List[ConversationTurn]] = None,
) -> tuple[str, int]:
    """Generate answer using OpenAI based on search results and conversation history."""
    if not results:
        return "I don't have enough information to answer that question.", 0

    context, question_results, reply_results = _build_context(results)

    system_content = f"{SYSTEM_PROMPT}\n\nInformation:\n{context}"

    messages: list[dict] = [{"role": "system", "content": system_content}]

    if conversation_history:
        for turn in conversation_history:
            messages.append({"role": "user", "content": turn.query})
            messages.append({"role": "assistant", "content": turn.answer})

    messages.append({"role": "user", "content": query})

    response = client_oa.chat.completions.create(model="gpt-4o-mini", messages=messages)

    answer: str = response.choices[0].message.content.strip()
    tokens_used: int = response.usage.total_tokens

    references: str = "\n\nReferences"
    for i, msg in enumerate(question_results, 1):
        references += f"\n{i}) {msg['link']}"

    return answer + references, tokens_used
