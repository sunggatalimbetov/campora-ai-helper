# Feature: Reply Threading in Group Chats

## Problem

Currently, the bot sends responses as standalone messages in group chats. When multiple people ask questions, it's impossible to tell which answer belongs to which question. This creates confusion in active group chats.

## Solution

Always use Telegram's reply-to feature in group chats so the bot's answer is visually linked to the original question. In DMs, current behavior (standalone reply) is fine since there's only one conversation thread.

## Technical Design

### Change

Replace `update.message.reply_text(answer)` with the same call — `reply_text()` already replies to the original message in python-telegram-bot. However, the "Searching..." status message should also be a reply.

The key change: ensure ALL bot responses in groups (including the "🔍 Searching..." message) reply to the user's original message using `reply_to_message_id`.

### In `commands.py` — `ask_command`:

`update.message.reply_text()` already sets `reply_to_message_id` automatically when used on a `Message` object. This is already the current behavior. Verify it works correctly.

### For Future @mention Handler:

When implementing the mention handler, ensure the same pattern:

```python
await update.message.reply_text(answer, reply_markup=keyboard)
```

### Edge Cases

- **Bot mentions without reply context**: If someone types `@bot_name question` mid-conversation, the bot replies to that specific message
- **Forwarded messages**: If a user forwards a message and asks about it, the bot replies to the forwarded message
- **Thread/topic groups**: Telegram supergroups with topics — replies should stay within the same topic. `reply_text()` handles this automatically

## Files to Change

- `src/handlers/commands.py` — verify `reply_text()` threads correctly in groups (likely already works)
- Future mention handler — ensure consistent reply behavior

## Verification

This may already work correctly since `reply_text()` replies to the triggering message by default. The main task is to **verify** and ensure consistency, especially for:

1. The "🔍 Searching..." intermediate message
2. The final answer message
3. Error messages

## Implementation Checklist

- [ ] Verify `reply_text()` in `ask_command` correctly replies to the user's message in groups
- [ ] Verify the "Searching..." message is also a reply, not a standalone message
- [ ] Test in a real group: ask a question → both "Searching..." and answer are threaded under the question
- [ ] Test with multiple questions from different users → each answer threads under correct question
- [ ] Document behavior for future mention handler

## Status

Planned
