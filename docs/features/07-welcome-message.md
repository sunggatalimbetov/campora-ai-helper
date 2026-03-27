# Feature: Welcome Message on Group Join

## Problem

When the bot is added to a group chat, nobody knows what it does, how to use it, or what commands are available. This leads to low adoption and confusion.

## Current State

A basic `track_chat_member` handler already exists in `main.py` (line 48) that sends an opt-out notice when the bot is added to a group. However, the current message only mentions opt-out — it doesn't explain the bot's purpose or how to use it.

## Solution

Enhance the existing welcome message to serve as a proper onboarding message that explains:
1. What the bot does (one-liner)
2. How to interact with it (`/ask`, mentions)
3. A quick usage example
4. Privacy note (opt-out option)

Keep it concise — max 5-6 lines to avoid being intrusive.

## Implementation

### Files to Change

- `main.py` — update `WELCOME_NOTICE` text and `track_chat_member` handler

### Updated Welcome Message

```python
WELCOME_NOTICE = (
    "👋 Привет! Я Campora AI — помогаю находить ответы на вопросы "
    "по истории переписки этой группы.\n\n"
    "Как использовать:\n"
    "• /ask <вопрос> — задать вопрос\n"
    "• /help — все команды\n\n"
    "Пример: /ask когда дедлайн по курсовой?\n\n"
    "Я отвечаю только на вопросы, связанные с учёбой. "
    "Если не хочешь, чтобы твои сообщения использовались — напиши /optout."
)
```

### Persistence Across Restarts

Currently `_notified_chats` is an in-memory set that resets on restart. To avoid re-sending:

- Option A (simple): Store notified `chat_id`s in a Supabase table `bot_group_settings`.
- Option B (minimal): Accept that a restart re-sends the message — it's infrequent and harmless.

Start with Option B; migrate to Option A when implementing Admin Commands (feature 12).

### Edge Cases

- Bot removed and re-added: should re-send the welcome message (user expectation)
- Bot promoted to admin: should NOT re-send if already in the group — check `old_chat_member.status`

## Implementation Checklist

- [ ] Update `WELCOME_NOTICE` text in `main.py`
- [ ] Update `track_chat_member` to check old vs new status (avoid duplicate sends on promotion)
- [ ] Test: add bot to group → verify welcome message appears
- [ ] Test: promote bot to admin → verify no duplicate message

## Status

Planned
