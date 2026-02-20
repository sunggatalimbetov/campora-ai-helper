from typing import List

from src.models.message import MessageDict
from src.services.message_search._clients import client_oa


def generate_answer(query: str, results: list) -> tuple[str, int]:
    """Generate answer using OpenAI based on search results."""
    if not results:
        return "I don't have enough information to answer that question.", 0

    # Separate original matches from replies
    question_results: List[MessageDict] = [msg for msg in results if not msg.get("is_reply", False)]
    reply_results: List[MessageDict] = [msg for msg in results if msg.get("is_reply", False)]

    # Build context with clear separation
    context_parts: List[str] = []

    if question_results:
        context_parts.append("Original relevant messages:")
        for i, msg in enumerate(question_results):
            similarity = msg.get("similarity", 0)
            context_parts.append(f"{i+1}. (Similarity: {similarity:.2f}) {msg['text']}")

    if reply_results:
        context_parts.append("\nReplies/Answers to these messages:")
        for i, msg in enumerate(reply_results):
            similarity = msg.get("similarity", 0)
            context_parts.append(f"Reply {i+1}. (Similarity: {similarity:.2f}) {msg['text']}")

    context: str = "\n".join(context_parts)

    print(question_results)
    print(f"\n\n{context}\n\n")

    prompt: str = f"""
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

		Information:
		{context}

		User's question: {query}

		Instructions:
		- Answer directly and naturally — never say things like "based on the provided context",
		  "в предоставленном контексте", "на основании предоставленного контекста",
		  "according to the information I have", or similar phrases
		- Prioritize information from replies/answers when available
		- Consider similarity scores when weighing the importance of information
		- Write your response in the same language as the user's question
		- Do NOT include any links in your answer - they will be added automatically
	"""

    response = client_oa.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt}])

    answer: str = response.choices[0].message.content.strip()
    tokens_used: int = response.usage.total_tokens

    # Add references in the exact format requested
    references: str = "\n\nReferences"
    for i, msg in enumerate(question_results, 1):
        references += f"\n{i}) {msg['link']}"

    return answer + references, tokens_used
