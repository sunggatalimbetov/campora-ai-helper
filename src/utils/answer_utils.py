"""Pure utility functions for answer processing.

This module has no heavy dependencies (no openai, no supabase) so it can
be imported directly in tests.
"""

from __future__ import annotations


def strip_references(answer: str) -> str:
    """Strip the references section appended to prior answers.

    References are always appended in English (see generate_answer),
    even when the answer body is in another language.
    """
    ref_marker = "\n\nReferences"
    if ref_marker in answer:
        return answer[: answer.index(ref_marker)]
    return answer


GROUP_CHAT_TYPES = {"group", "supergroup", "channel"}


def build_references(question_results: list[dict], chat_type: str) -> str:
    """Build the references string based on chat type.

    Private: full numbered list. Group: condensed top 2 on one line.
    """
    if chat_type == "private":
        references = "\n\nReferences"
        for i, msg in enumerate(question_results, 1):
            references += f"\n{i}) {msg['link']}"
        return references

    top_refs = question_results[:2]
    if top_refs:
        return "\n\nRef: " + " | ".join(msg["link"] for msg in top_refs)
    return ""


def filter_by_similarity(results: list[dict], threshold: float) -> list[dict]:
    """Drop search results below the similarity threshold."""
    return [r for r in results if r.get("semantic_similarity", 0) >= threshold]
