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


def filter_by_similarity(results: list[dict], threshold: float) -> list[dict]:
    """Drop search results below the similarity threshold."""
    return [r for r in results if r.get("semantic_similarity", 0) >= threshold]
