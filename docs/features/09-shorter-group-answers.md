# Feature: Shorter Answers in Group Chats

## Problem

The current answer format (full explanation + references) works well in DMs where the user expects a detailed response. In group chats, long messages disrupt conversation flow, get ignored, and feel spammy.

## Solution

Adjust the system prompt and response format based on chat type:
- **DMs**: Keep current detailed answers with full references
- **Groups**: 2-3 sentence summary + condensed references + hint to DM for more detail

## Technical Design

### Modify `generate_answer.py`

Add a `chat_type` parameter to `generate_answer()` that switches the system prompt behavior:

```python
GROUP_PROMPT_ADDENDUM = """
IMPORTANT — Group chat mode:
You are answering in a group chat. Keep your response very concise:
- Maximum 2-3 sentences
- Give the direct answer only, no elaboration
- If the topic is complex, give the short answer and suggest: "Напиши мне в ЛС для подробного ответа" (or equivalent in the user's language)
"""


def generate_answer(
    query: str,
    results: list,
    conversation_history=None,
    chat_type: str = "private",  # NEW parameter
) -> tuple[str, int]:
    system_content = f"{SYSTEM_PROMPT}\n\nInformation:\n{context}"

    if chat_type != "private":
        system_content += GROUP_PROMPT_ADDENDUM

    # ... rest unchanged
```

### Modify References Format for Groups

In group chats, show only 1-2 top references instead of all:

```python
if chat_type == "private":
    # Full references (current behavior)
    references = "\n\nReferences"
    for i, msg in enumerate(question_results, 1):
        references += f"\n{i}) {msg['link']}"
else:
    # Condensed: only top 2 references
    top_refs = question_results[:2]
    if top_refs:
        references = "\n\nRef: " + " | ".join(msg["link"] for msg in top_refs)
    else:
        references = ""
```

### Pass Chat Type Through the Call Chain

Update callers to pass `chat_type`:

- `src/handlers/messages.py` → `dm_handler` already knows it's private
- `src/handlers/commands.py` → `ask_command` can check `update.effective_chat.type`

```python
# In ask_command:
chat_type = update.effective_chat.type  # "group", "supergroup", or "private"
answer, tokens_used = generate_answer(query, results, history, chat_type=chat_type)
```

## Files to Change

- `src/services/message_search/generate_answer.py` — add `chat_type` param, group prompt, condensed refs
- `src/handlers/commands.py` — pass `chat_type` to `generate_answer()`
- `src/handlers/messages.py` — pass `chat_type="private"` explicitly (for clarity)

## Implementation Checklist

- [ ] Add `GROUP_PROMPT_ADDENDUM` to `generate_answer.py`
- [ ] Add `chat_type` parameter to `generate_answer()`
- [ ] Implement condensed references for group mode
- [ ] Update `ask_command` to pass `chat_type`
- [ ] Update `dm_handler` to pass `chat_type="private"`
- [ ] Test: same question in DM → full answer; in group → concise answer
- [ ] Verify references are shorter in group mode

## Status

Planned
