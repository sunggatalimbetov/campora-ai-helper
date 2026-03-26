from __future__ import annotations

import re
from typing import Iterable

from telegram import MessageEntity


def should_process_message(text: str) -> bool:
    """Filter messages based on content quality."""
    if not text or not text.strip():
        return False

    text = text.strip()

    # Skip if too short (less than 16 characters)
    if len(text) < 16:
        return False

    # Skip if only one word (no spaces after stripping)
    if " " not in text:
        return False

    # Skip if contains only emojis and whitespace
    # Remove all emojis and special characters, check if anything meaningful remains
    text_without_emojis = re.sub(r"[^\w\s]", "", text)  # Remove all non-alphanumeric except spaces
    text_without_emojis = re.sub(r"\s+", " ", text_without_emojis).strip()  # Clean up spaces

    # If after removing emojis/symbols, we have less than 10 chars, skip
    if len(text_without_emojis) < 10:
        return False

    # Skip if text is mostly numbers (like timestamps, IDs)
    if re.match(r"^[\d\s\-:./]+$", text):
        return False

    return True


def iter_matching_mentions(text: str, entities: Iterable[MessageEntity] | None, bot_username: str) -> list[tuple[int, int]]:
    """Return ranges for @mentions that target this bot."""
    if not text or not entities or not bot_username:
        return []

    normalized_username = bot_username.lstrip("@").lower()
    matching_ranges: list[tuple[int, int]] = []

    for entity in entities:
        if entity.type != MessageEntity.MENTION:
            continue

        mention_text = text[entity.offset : entity.offset + entity.length]
        if mention_text.lstrip("@").lower() == normalized_username:
            matching_ranges.append((entity.offset, entity.offset + entity.length))

    return matching_ranges


def extract_mentioned_query(text: str, entities: Iterable[MessageEntity] | None, bot_username: str) -> str | None:
    """Extract the user question from a group message that mentions this bot."""
    matching_ranges = iter_matching_mentions(text, entities, bot_username)
    if not matching_ranges:
        return None

    remaining_parts: list[str] = []
    last_index = 0

    for start, end in sorted(matching_ranges):
        if last_index < start:
            remaining_parts.append(text[last_index:start])
        last_index = end

    if last_index < len(text):
        remaining_parts.append(text[last_index:])

    cleaned_query = re.sub(r"\s+", " ", "".join(remaining_parts)).strip(" ,:-\n\t")
    return cleaned_query or ""
