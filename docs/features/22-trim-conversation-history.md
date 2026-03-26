# Feature: Trim Conversation History

## Problem

In `generate_answer.py` (lines 85-88), the full text of previous answers — including the appended references section — is injected as assistant turns in the LLM context. A single previous answer can be 300-500 tokens. With `CONVERSATION_MAX_TURNS` previous turns, this adds significant token overhead and dilutes the current query's context.

The query rewriting step (`rewrite_query.py`) already extracts the conversational intent from history. The answer generation step doesn't need the full verbatim history — it needs enough context to maintain coherence, not to re-read every prior answer.

## Solution

Before injecting conversation history into the answer generation prompt, trim each prior answer to a concise summary and strip references.

## Technical Design

### Approach: Strip References + Truncate

The simplest approach — no extra LLM calls:

```python
def _trim_answer(answer: str, max_chars: int = 300) -> str:
    """Strip references section and truncate to max_chars."""
    # Remove references block
    ref_marker = "\n\nReferences"
    if ref_marker in answer:
        answer = answer[:answer.index(ref_marker)]

    # Truncate if still long
    if len(answer) > max_chars:
        answer = answer[:max_chars].rsplit(" ", 1)[0] + "..."

    return answer
```

### Integration

In `generate_answer.py`, when building the messages list:

```python
if conversation_history:
    for turn in conversation_history:
        messages.append({"role": "user", "content": turn.query})
        messages.append({"role": "assistant", "content": _trim_answer(turn.answer)})
```

### Token Impact

- Before: ~300-500 tokens per prior turn × up to N turns
- After: ~60-100 tokens per prior turn
- Savings: 200-400 tokens per turn, which means faster generation and lower cost

### Alternative: LLM Summarization

A more sophisticated approach would summarize each prior answer via an LLM call. This is overkill for now — stripping references and truncating is 90% of the win with zero added latency.

## Files to Change

- `src/services/message_search/generate_answer.py` — add `_trim_answer()` and use it when building history messages

## Implementation Checklist

- [ ] Add `_trim_answer()` function to `generate_answer.py`
- [ ] Apply trimming when injecting conversation history
- [ ] Test: multi-turn conversation still maintains coherence
- [ ] Test: verify token usage decreases on follow-up questions
- [ ] Run evaluation on multi-turn test cases if available

## Status

Planned
