# Feature: Typing Indicator

## Problem

In group chats, after a user asks a question, there's a silent gap while the bot searches and generates an answer (typically 3-8 seconds). This silence makes the bot feel broken or unresponsive, especially for first-time users.

## Solution

Replace or supplement the "🔍 Searching..." text message with Telegram's native "typing..." indicator (chat action). This is less intrusive than a text message and is the expected UX pattern for bots.

## Technical Design

### Approach

Use `update.effective_chat.send_action(ChatAction.TYPING)` to show the typing indicator. This lasts ~5 seconds per call and can be refreshed.

### Two Options

**Option A — Replace "Searching..." message with typing action (recommended for groups):**

```python
from telegram.constants import ChatAction

# In group handler:
await update.effective_chat.send_action(ChatAction.TYPING)
# ... perform search and answer generation ...
await update.message.reply_text(answer)
```

**Option B — Keep "Searching..." in DMs, use typing in groups:**

```python
if update.effective_chat.type == "private":
    await update.message.reply_text("🔍 Searching, please wait...")
else:
    await update.effective_chat.send_action(ChatAction.TYPING)
```

Recommend **Option B** — DM users expect a text acknowledgment, group users prefer a subtle indicator.

### Long-Running Queries

If search + generation takes longer than 5 seconds, the typing indicator expires. To handle this:

```python
import asyncio

async def send_typing_periodically(chat, stop_event):
    """Send typing action every 4 seconds until stopped."""
    while not stop_event.is_set():
        await chat.send_action(ChatAction.TYPING)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=4)
        except asyncio.TimeoutError:
            continue
```

However, this adds complexity. Start simple (single typing action) and only add periodic refresh if users report the indicator disappearing.

## Files to Change

- `src/handlers/commands.py` — replace "Searching..." with typing action in `ask_command`
- `src/handlers/messages.py` — keep "Searching..." text in `dm_handler` (DM context)
- Future mention handler — use typing action

## Implementation Checklist

- [ ] Import `ChatAction` from `telegram.constants`
- [ ] In `ask_command`: replace "Searching..." message with `send_action(ChatAction.TYPING)` for group chats
- [ ] Keep "Searching..." text message in `dm_handler`
- [ ] Test: ask in group → see typing indicator instead of text message
- [ ] Test: ask in DM → still see "🔍 Searching..." text
- [ ] Evaluate if periodic typing refresh is needed (based on typical response times)

## Status

Implemented
