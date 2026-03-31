from datetime import date
from typing import List, Optional

from src.models.message import MessageDict
from src.services.conversation import ConversationTurn
from src.services.language import get_string
from src.services.message_search._clients import client_oa
from src.utils.answer_utils import GROUP_CHAT_TYPES, build_references, trim_answer_for_history

SYSTEM_PROMPT_TEMPLATE = """\
You are a helpful assistant for university students. Answer questions about university life \
(academics, exams, deadlines, enrollment, housing, campus life, etc.) using ONLY the \
information below. Respond naturally — never mention "context" or "provided information".

Current date: {current_date}

DATE RULES — apply to ANY time-sensitive question (deadlines, offers, exams, "когда", "when"):
1. Always cite the source date: "По информации от [дата], ..."
2. If ALL sources are older than 6 months → add: "эта информация может быть неактуальной"
3. NEVER state old relative dates ("завтра", "в мае", "через неделю") as current facts
4. If no source is from the current academic year → say you don't have current info

KNOWN FACTS — use these to sanity-check sources (reject claims that violate these):
- NUET: max score 240, Foundation minimum ~130-150 (varies by year)
- SAT: max score 1600
- IELTS: max score 9.0, each band 0-9
- NU has ~15 undergraduate majors across SSH, SE, SMG, SEDS, SoM schools
- If a source claims a score above these maximums, it's likely sarcasm — do not take it literally

TOPIC FILTER:
If the question is clearly off-topic (dating, cooking, entertainment, politics unrelated \
to university), decline in the user's language: "I can only help with university-related questions."

ANSWER RULES:
- Prioritize replies over original messages — replies usually contain the actual answers
- Higher similarity scores = more relevant
- Newer messages are more reliable for time-sensitive topics
- If you can only provide a partial answer, say so (e.g. "вот некоторые специальности, \
но это не полный список")
- Write in the language requested below
- Do NOT include links — they are added automatically"""


def _get_system_prompt() -> str:
    current_date = date.today().isoformat()
    return SYSTEM_PROMPT_TEMPLATE.format(current_date=current_date)

GROUP_PROMPT_ADDENDUM = """
IMPORTANT — Group chat mode:
You are answering in a group chat. Keep your response very concise:
- Maximum 2-3 sentences
- Give the direct answer only, no elaboration
- If the topic is complex, give the short answer and suggest the user message you directly for a detailed response"""


def _build_context(results: list) -> tuple[str, List[MessageDict], List[MessageDict]]:
    raw_question_results: List[MessageDict] = [msg for msg in results if not msg.get("is_reply", False)]
    reply_results: List[MessageDict] = [msg for msg in results if msg.get("is_reply", False)]
    replies_by_parent: dict[int, List[MessageDict]] = {}
    reply_ids = {reply["id"] for reply in reply_results if reply.get("id") is not None}

    for reply in reply_results:
        parent_id = reply.get("replying_to")
        if parent_id is None:
            continue
        replies_by_parent.setdefault(parent_id, []).append(reply)

    question_results = [msg for msg in raw_question_results if msg.get("id") not in reply_ids]

    context_parts: List[str] = []

    if question_results:
        for i, msg in enumerate(question_results):
            similarity = msg.get("similarity", 0)
            date_str = msg.get("created_at", "")
            date_label = f" [{date_str[:10]}]" if date_str else ""
            context_parts.append(f"Thread {i+1} (Similarity: {similarity:.2f}){date_label}:")
            context_parts.append(f"  Message: {msg['text']}")

            for reply in replies_by_parent.get(msg["id"], []):
                reply_date = reply.get("created_at", "")
                reply_date_label = f" [{reply_date[:10]}]" if reply_date else ""
                context_parts.append(f"  Reply{reply_date_label}: {reply['text']}")

    return "\n".join(context_parts), question_results, reply_results


DECLINE_PHRASES = [
    "i can only help with university",
    "я могу помочь только с вопросами",
    "мен тек университетке",
]


def is_declined(answer: str) -> bool:
    """Check if the LLM declined to answer (off-topic question)."""
    return any(phrase in answer.lower() for phrase in DECLINE_PHRASES)


def build_messages(
    query: str,
    results: list,
    conversation_history: Optional[List[ConversationTurn]] = None,
    answer_language: str = "ru",
    chat_type: str = "private",
) -> tuple[list[dict], List[MessageDict]]:
    """Build the OpenAI messages array and return question results for references.

    Returns (messages, question_results) where question_results are the
    non-reply search results needed for building references later.
    """
    context, question_results, reply_results = _build_context(results)

    system_prompt = _get_system_prompt()
    system_content = f"{system_prompt}\n\nAnswer language: {answer_language}\n\nInformation:\n{context}"

    if chat_type in GROUP_CHAT_TYPES:
        system_content += GROUP_PROMPT_ADDENDUM

    messages: list[dict] = [{"role": "system", "content": system_content}]

    if conversation_history:
        for turn in conversation_history:
            messages.append({"role": "user", "content": turn.query})
            messages.append({"role": "assistant", "content": trim_answer_for_history(turn.answer)})

    messages.append({"role": "user", "content": query})

    return messages, question_results


def generate_answer(
    query: str,
    results: list,
    conversation_history: Optional[List[ConversationTurn]] = None,
    answer_language: str = "ru",
    chat_type: str = "private",
) -> tuple[str, int]:
    """Generate answer using OpenAI based on search results and conversation history."""
    if not results:
        return get_string(answer_language, "no_results"), 0

    messages, question_results = build_messages(query, results, conversation_history, answer_language, chat_type)

    response = client_oa.chat.completions.create(model="gpt-4o-mini", messages=messages)

    answer: str = response.choices[0].message.content.strip()
    tokens_used: int = response.usage.total_tokens

    if not is_declined(answer):
        references = build_references(question_results, chat_type, language=answer_language)
        answer = answer + references

    return answer, tokens_used
