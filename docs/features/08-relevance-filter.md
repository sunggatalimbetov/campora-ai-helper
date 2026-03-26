# Feature: Relevance Filter for Group Messages

## Problem

In group chats, the bot will receive many messages that have nothing to do with university life (casual chat, memes, off-topic discussions). Responding to every irrelevant message with a "I can't help with that" reply would spam the group and annoy users.

## Solution

Add a lightweight relevance classifier that runs before the main search pipeline. In group chats:
- **Relevant** → proceed with search + answer
- **Not relevant** → silently skip, no response

In DMs, keep current behavior — the system prompt in `generate_answer.py` already politely declines off-topic questions.

## Technical Design

### Approach: LLM-based Classification

Use a fast, cheap LLM call (gpt-4o-mini) with a focused prompt to classify relevance. This is more robust than keyword matching for multilingual content (Russian, Kazakh, English).

### New Service

Create `src/services/relevance_filter.py`:

```python
from src.services.message_search._clients import client_oa


def is_university_related(message: str) -> bool:
    """
    Classify whether a message is related to university/student life.
    Returns True if relevant, False if off-topic.
    """
    response = client_oa.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=5,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a classifier. Determine if the user's message is related to "
                    "university or student life (academics, exams, deadlines, enrollment, "
                    "schedules, student services, housing, campus, scholarships, etc.).\n"
                    "Reply with exactly YES or NO."
                ),
            },
            {"role": "user", "content": message},
        ],
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer.startswith("YES")
```

### Integration Point

The relevance check should be called in the group message handler (currently `ask_command` in `commands.py`, and the future `@mention` handler) **before** the search pipeline:

```python
# In group message/mention handler:
if not is_university_related(query):
    return  # silently skip

# ... proceed with search + answer
```

### Cost Impact

- ~20-30 tokens per classification call
- At gpt-4o-mini pricing: ~$0.0003 per 1000 classifications
- Negligible compared to the full search + answer pipeline

### Edge Cases

- **Borderline questions**: The prompt should err on the side of "relevant" — better to answer a borderline question than ignore a valid one
- **Commands**: `/ask`, `/help`, `/new` should bypass the filter entirely (they already have their own handlers)
- **Short messages**: Single-word messages like "thanks" or "ok" — classify as not relevant
- **Mixed language**: The classifier handles Russian/Kazakh/English natively via the LLM

## Files to Change

- Create `src/services/relevance_filter.py` — new classifier service
- `src/handlers/commands.py` — add filter call in `ask_command` for group context
- Future group mention handler — integrate filter there too

## Implementation Checklist

- [ ] Create `src/services/relevance_filter.py` with `is_university_related()`
- [ ] Add relevance check in `ask_command` (only for group chats)
- [ ] Test with university-related questions → bot responds
- [ ] Test with off-topic messages → bot stays silent
- [ ] Test with borderline messages → bot errs toward responding
- [ ] Verify DM behavior unchanged (no filter applied)

## Status

Planned
