# Feature: Similarity Threshold Filter

## Problem

All 5 search results are passed to the LLM regardless of their similarity score. A result with 0.35 semantic similarity is essentially noise — it's unlikely to contain relevant information and wastes tokens. This is different from feature 08 (Relevance Filter), which filters by topic relevance before search. This feature filters by search quality after search.

## Current State

The evaluation shows average top similarity of 0.83, but lower-ranked results can score well below 0.5. These low-quality results dilute the context and can mislead the LLM.

## Solution

After hybrid search, drop results whose `semantic_similarity` score falls below a configurable threshold. This reduces noise, saves tokens, and speeds up answer generation.

## Technical Design

### Implementation

Add filtering in `search_messages_hybrid.py` after results are returned, or in `generate_answer.py` before building context.

Recommend filtering at the search level so reply fetching also benefits (fewer parent messages = fewer replies to fetch).

```python
# In search_messages_hybrid.py, after getting results:
SIMILARITY_THRESHOLD = 0.45

results = [r for r in results if r.get("semantic_similarity", 0) >= SIMILARITY_THRESHOLD]
```

### Threshold Choice

- **0.3** — very permissive, keeps almost everything (current eval shows 98% pass at 0.3)
- **0.45** — moderate, drops clearly irrelevant noise while keeping borderline results
- **0.6** — aggressive, might drop valid results for uncommon topics

Start with **0.45** and make it configurable via `settings.py`. Monitor zero-result rate — if it increases above 5%, lower the threshold.

### Configuration

```python
# settings.py
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
```

### Edge Case: All Results Below Threshold

If filtering removes all results, treat it the same as zero results — show the "no relevant messages found" response. Don't fall back to showing low-quality results.

## Files to Change

- `src/services/message_search/search_messages_hybrid.py` — add threshold filter after search
- `src/config/settings.py` — add `SIMILARITY_THRESHOLD` config

## Implementation Checklist

- [ ] Add `SIMILARITY_THRESHOLD` to settings
- [ ] Filter results by threshold in `search_messages_hybrid.py`
- [ ] Test: query with clear match → results returned as before
- [ ] Test: vague/off-topic query → low-similarity results filtered out
- [ ] Run evaluation suite — compare zero-result rate and keyword hit rate
- [ ] Adjust threshold if zero-result rate exceeds 5%
- [ ] Validate filtered result sets against Supabase data before merge

## Status

Implemented
