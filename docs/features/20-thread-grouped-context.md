# Feature: Thread-Grouped Context for LLM

## Problem

In `generate_answer.py`, the `_build_context` function splits search results into two separate sections: "Original relevant messages" and "Replies/Answers." This breaks the conversational thread structure — the LLM sees a question and its answer in completely different parts of the context, making it harder to reason about Q&A pairs.

Note: This is different from feature 10 (Reply Threading in Group Chats), which is about Telegram's reply UI. This feature is about how we structure context sent to the LLM.

## Current Code

```python
# Current: splits by type
"Original relevant messages:"
"1. (Similarity: 0.92) When is the scholarship deadline?"
"2. (Similarity: 0.78) How to apply for housing?"

"Replies/Answers to these messages:"
"Reply 1. (Similarity: 0.92) December 15, bring your transcript"
"Reply 2. (Similarity: 0.78) Go to building 3, room 101"
```

The LLM has to mentally match Reply 1 to Message 1 by position — fragile and error-prone.

## Solution

Group each message with its replies as a thread, so the LLM sees the full conversation unit together.

## Technical Design

### New Context Format

```
Thread 1 (Similarity: 0.92) [2025-12-01]:
  Message: "When is the scholarship deadline?"
  → Reply: "December 15, bring your transcript"
  → Reply: "Also you need GPA above 3.0"

Thread 2 (Similarity: 0.78) [2025-11-28]:
  Message: "How to apply for housing?"
  → Reply: "Go to building 3, room 101"
```

### Updated `_build_context`

```python
def _build_context(results: list) -> tuple[str, list, list]:
    # Separate parent messages and replies
    parents = [msg for msg in results if not msg.get("is_reply", False)]
    replies = [msg for msg in results if msg.get("is_reply", False)]

    # Group replies by parent
    replies_by_parent = {}
    for reply in replies:
        parent_id = reply.get("replying_to")
        replies_by_parent.setdefault(parent_id, []).append(reply)

    context_parts = []
    for i, msg in enumerate(parents, 1):
        similarity = msg.get("similarity", 0)
        date_str = msg.get("created_at", "")
        date_label = f" [{date_str[:10]}]" if date_str else ""

        context_parts.append(f"Thread {i} (Similarity: {similarity:.2f}){date_label}:")
        context_parts.append(f"  Message: {msg['text']}")

        for reply in replies_by_parent.get(msg["id"], []):
            reply_date = reply.get("created_at", "")
            reply_date_label = f" [{reply_date[:10]}]" if reply_date else ""
            context_parts.append(f"  → Reply{reply_date_label}: {reply['text']}")

    return "\n".join(context_parts), parents, replies
```

### System Prompt Update

Update the system prompt instruction from:

```
The information includes both original relevant messages and their replies/answers.
Pay special attention to the replies as they often contain the actual answers to questions.
```

To:

```
The information is organized as threads. Each thread contains an original message
and its replies. Replies often contain the actual answers — prioritize them.
```

## Expected Impact

- LLM can directly see which reply answers which question
- Should improve keyword hit rate (currently 32%) as the model can better identify relevant answer content
- Slightly fewer tokens (no duplicate headers)

## Files to Change

- `src/services/message_search/generate_answer.py` — rewrite `_build_context` and update system prompt

## Implementation Checklist

- [ ] Rewrite `_build_context` to group messages as threads
- [ ] Update system prompt to reference thread structure
- [ ] Test: verify generated answers correctly use reply content
- [ ] Run evaluation suite and compare keyword hit rate before/after
- [ ] Verify token usage doesn't increase significantly

## Status

Planned
