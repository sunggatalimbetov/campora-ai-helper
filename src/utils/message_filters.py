import re


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
