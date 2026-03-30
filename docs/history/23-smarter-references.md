# Feature: Smarter References

## Problem

In `generate_answer.py` (lines 97-99), references are appended blindly — every parent message link is included regardless of whether the answer actually used that information. This produces a wall of URLs with no context about what each link contains. Users can't tell which reference is worth clicking.

```python
# Current
references = "\n\nReferences"
for i, msg in enumerate(question_results, 1):
    references += f"\n{i}) {msg['link']}"
```

## Solution

Add brief labels to references and only include messages that are likely relevant (above similarity threshold). Optionally, let the LLM indicate which sources it used.

## Technical Design

### Approach: Labeled References with Preview

```python
def _build_references(question_results: list) -> str:
    if not question_results:
        return ""

    lines = ["\n\n📎 Источники:"]
    for i, msg in enumerate(question_results, 1):
        # Truncate message text for preview
        preview = msg["text"][:80].replace("\n", " ")
        if len(msg["text"]) > 80:
            preview += "..."
        lines.append(f"{i}. [{preview}]({msg['link']})")

    return "\n".join(lines)
```

This gives users a snippet of what each link contains so they can decide if it's worth clicking.

### Example Output

Before:
```
References
1) https://t.me/group/12345
2) https://t.me/group/12346
3) https://t.me/group/12347
```

After:
```
📎 Источники:
1. [Дедлайн по стипендии — 15 декабря, нужно принести...](https://t.me/group/12345)
2. [Для подачи документов нужен GPA выше 3.0...](https://t.me/group/12346)
```

### Filtering

Only include references for messages above the similarity threshold (ties into feature 21). If a message was filtered out of the context, its link shouldn't appear in references either.

### Telegram Markdown

Telegram supports inline links with `[text](url)` in MarkdownV2 mode. Need to ensure `reply_text` uses `parse_mode="MarkdownV2"` and properly escapes special characters.

If MarkdownV2 escaping is too fragile, fall back to plain text with the preview as a label:

```
📎 Источники:
1. Дедлайн по стипендии — 15 декабря, нужно принести...
   https://t.me/group/12345
```

## Files to Change

- `src/services/message_search/generate_answer.py` — replace reference building logic

## Implementation Checklist

- [ ] Create `_build_references()` with text previews
- [ ] Replace current reference logic in `generate_answer()`
- [ ] Test with MarkdownV2 parsing in Telegram
- [ ] Fallback to plain text if markdown causes issues
- [ ] Verify references only include messages that were in the LLM context
- [ ] Validate reference output against Supabase-backed retrieval results before merge

## Status

Implemented
