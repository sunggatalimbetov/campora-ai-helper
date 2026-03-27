"""Pure utility functions for answer processing.

This module has no heavy dependencies (no openai, no supabase) so it can
be imported directly in tests.
"""

from __future__ import annotations


_REFERENCE_MARKERS = ("\n\n📎 Sources:", "\n\n📎 Источники:", "\n\n📎 Дереккөздер:", "\n\nReferences")


def strip_references(answer: str) -> str:
    """Strip the references section appended to prior answers."""
    for marker in _REFERENCE_MARKERS:
        if marker in answer:
            return answer[: answer.index(marker)]
    return answer


GROUP_CHAT_TYPES = {"group", "supergroup", "channel"}

_PREVIEW_MAX_CHARS = 80

REFERENCES_HEADER = {"ru": "📎 Источники:", "kk": "📎 Дереккөздер:", "en": "📎 Sources:"}


def _escape_markdown(text: str) -> str:
    """Escape characters that break Telegram Markdown v1 inside link labels."""
    for ch in ("[]", "()", "`"):
        for c in ch:
            text = text.replace(c, "")
    return text


def _message_preview(text: str) -> str:
    """Return a truncated, single-line preview of a message."""
    preview = text[:_PREVIEW_MAX_CHARS].replace("\n", " ")
    if len(text) > _PREVIEW_MAX_CHARS:
        preview = preview.rsplit(" ", 1)[0] + "..."
    return _escape_markdown(preview)


def build_references(question_results: list[dict], chat_type: str, language: str = "en") -> str:
    """Build references string with message previews.

    Private: labeled inline links. Group: condensed top 2.
    """
    if not question_results:
        return ""

    header = REFERENCES_HEADER.get(language, REFERENCES_HEADER["en"])

    if chat_type in GROUP_CHAT_TYPES:
        top_refs = question_results[:2]
        lines = [f"\n\n{header}"]
        for i, msg in enumerate(top_refs, 1):
            preview = _message_preview(msg["text"])
            lines.append(f"{i}. [{preview}]({msg['link']})")
        return "\n".join(lines)

    lines = [f"\n\n{header}"]
    for i, msg in enumerate(question_results, 1):
        preview = _message_preview(msg["text"])
        lines.append(f"{i}. [{preview}]({msg['link']})")
    return "\n".join(lines)


def filter_by_similarity(results: list[dict], threshold: float) -> list[dict]:
    """Drop search results below the similarity threshold."""
    return [r for r in results if r.get("semantic_similarity", 0) >= threshold]
