# Feature: Inline Mode

## Problem

Currently the bot can only be used in groups where it's been added as a member, or in DMs. Users who want to quickly look something up in a different chat (or a chat where the bot isn't added) have no way to access it.

## Solution

Implement Telegram's inline mode, allowing users to type `@campora_ai_bot <question>` in any chat to get a quick answer without the bot being a member of that group.

## Technical Design

### How Inline Mode Works

1. User types `@campora_ai_bot when is the exam?` in any chat
2. Telegram sends an `InlineQuery` to the bot
3. Bot searches and returns results as `InlineQueryResult` cards
4. User selects a result → it gets posted in the chat

### Handler

Create `src/handlers/inline.py`:

```python
from uuid import uuid4
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ContextTypes

from src.services.message_search import search_messages
from src.services.message_search.generate_answer import generate_answer


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries (@bot_name query)."""
    query = update.inline_query.query.strip()
    if not query or len(query) < 3:
        return  # too short to search

    try:
        results, _ = search_messages(query)

        if not results:
            await update.inline_query.answer([
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="No results found",
                    input_message_content=InputTextMessageContent(
                        "❌ No relevant messages found."
                    ),
                )
            ])
            return

        # Generate a concise answer (use group-style short answers)
        answer, _ = generate_answer(query, results, chat_type="group")

        inline_results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Campora AI Answer",
                description=answer[:100] + "..." if len(answer) > 100 else answer,
                input_message_content=InputTextMessageContent(answer),
            )
        ]

        await update.inline_query.answer(inline_results, cache_time=60)

    except Exception as e:
        print(f"Error handling inline query: {e}")
```

### Registration in `main.py`

```python
from telegram.ext import InlineQueryHandler
from src.handlers.inline import inline_query_handler

app.add_handler(InlineQueryHandler(inline_query_handler))
```

### BotFather Configuration

Inline mode must be enabled via @BotFather:
1. `/setinline` — set the inline placeholder text (e.g., "Ask a university question...")
2. This is a one-time manual step

### Rate Limiting

Inline queries can be very frequent (Telegram sends one per keystroke with debouncing). Apply rate limiting:
- Minimum query length: 3 characters
- Cache results for 60 seconds (`cache_time=60`)
- Apply per-user rate limiting

### Limitations

- No conversation history in inline mode (stateless by design)
- No group-scoped search (no group context available)
- Results are shorter (inline cards have limited space)
- No feedback mechanism (no inline keyboard in inline results)

## Files to Change

- Create `src/handlers/inline.py` — inline query handler
- `main.py` — register `InlineQueryHandler`
- BotFather — enable inline mode (manual step)

## Dependencies

- Feature 09 (Shorter Group Answers) — reuses `chat_type="group"` for concise answers

## Implementation Checklist

- [ ] Enable inline mode in BotFather
- [ ] Create `src/handlers/inline.py`
- [ ] Register `InlineQueryHandler` in `main.py`
- [ ] Add minimum query length check (3 chars)
- [ ] Add rate limiting for inline queries
- [ ] Test: type `@bot question` in any chat → see answer card
- [ ] Test: select answer → posted in chat
- [ ] Test: short query (< 3 chars) → no results

## Status

Planned
