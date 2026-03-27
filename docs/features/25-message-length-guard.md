# Feature: Message Length Guard

## Problem

Telegram enforces a 4096-character limit per message. If the LLM generates a long answer and references are appended, the total can exceed this limit, causing `reply_text()` to raise a `BadRequest` error. The bot then falls into the generic error handler and the user sees "something went wrong" instead of their answer.

## Solution

Before sending, check message length. If it exceeds Telegram's limit, split the message into multiple parts.

## Technical Design

### Approach: Split at Natural Boundaries

```python
TELEGRAM_MAX_LENGTH = 4096

def split_message(text: str, max_length: int = TELEGRAM_MAX_LENGTH) -> list[str]:
    """Split a message into chunks that fit within Telegram's limit."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Find a natural split point (paragraph, then sentence, then word)
        split_at = text.rfind("\n\n", 0, max_length)
        if split_at == -1:
            split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = text.rfind(" ", 0, max_length)
        if split_at == -1:
            split_at = max_length

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks
```

### Integration

Create a helper that wraps `reply_text`:

```python
async def safe_reply(message, text, **kwargs):
    """Send a reply, splitting into multiple messages if needed."""
    chunks = split_message(text)
    last_msg = None
    for chunk in chunks:
        last_msg = await message.reply_text(chunk, **kwargs)
    return last_msg
```

Replace `update.message.reply_text(answer, reply_markup=keyboard)` with:

```python
chunks = split_message(answer)
for i, chunk in enumerate(chunks):
    is_last = i == len(chunks) - 1
    if is_last and interaction_id:
        await update.message.reply_text(chunk, reply_markup=keyboard)
    else:
        await update.message.reply_text(chunk)
```

The feedback keyboard is only attached to the last chunk.

### Where References Go

References should be in the last chunk. Since they're appended after the answer in `generate_answer.py`, they'll naturally end up at the end. If splitting occurs, references may end up in their own chunk — this is fine.

### Edge Case: Markdown Splitting

If using `parse_mode="MarkdownV2"`, splitting mid-formatting (e.g., inside `**bold**`) will break rendering. For now, the bot doesn't use parse_mode for answers, so this isn't an issue. If parse_mode is added later, the split function will need to be markdown-aware.

## Files to Change

- Create `src/utils/telegram.py` — `split_message()` and `safe_reply()` helpers
- `src/handlers/messages.py` — use `safe_reply` or split logic
- `src/handlers/commands.py` — use `safe_reply` or split logic

## Implementation Checklist

- [ ] Create `split_message()` utility function
- [ ] Integrate into `dm_handler` and `ask_command`
- [ ] Ensure feedback keyboard attaches to last chunk only
- [ ] Test: short answer → sent as single message (no change)
- [ ] Test: answer exceeding 4096 chars → splits cleanly at paragraph/sentence boundary
- [ ] Test: feedback buttons still work on split messages

## Status

Implemented
