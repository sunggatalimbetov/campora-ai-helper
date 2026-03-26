# Feature: Batch Reply Fetching (Fix N+1 Queries)

## Problem

In `search_messages_hybrid.py` (lines 63-78), after retrieving search results, the code fetches replies for each result in a separate Supabase query. With 5 search results, that's 5 additional round-trips to the database. This N+1 pattern is the biggest contributor to response time regression (2.8s → 10.16s as the database grew).

## Current Code

```python
for msg in messages:
    enhanced_results.append(msg)
    replies_response = supabase.table("messages") \
        .select("*") \
        .eq("reply_to_message_id", msg["id"]) \
        .eq("chat_id", msg["chat_id"]) \
        .execute()
    # ... append each reply
```

5 messages × 1 query each = 5 sequential network round-trips (~200-500ms each).

## Solution

Replace the per-message reply queries with a single batch query using Supabase's `in_` filter.

## Technical Design

### Batch Query

```python
# Collect all message IDs
message_ids = [msg["id"] for msg in messages]

# Single query for all replies
replies_response = supabase.table("messages") \
    .select("*") \
    .in_("reply_to_message_id", message_ids) \
    .execute()

# Group replies by parent message ID
replies_by_parent = {}
for reply in replies_response.data:
    parent_id = reply["reply_to_message_id"]
    replies_by_parent.setdefault(parent_id, []).append(reply)

# Build enhanced results
enhanced_results = []
for msg in messages:
    enhanced_results.append(msg)
    for reply in replies_by_parent.get(msg["id"], []):
        enhanced_results.append({
            **reply,
            "is_reply": True,
            "replying_to": msg["id"],
            "similarity": msg.get("similarity", 0),
        })
```

### Alternative: SQL-Level Join

An even faster approach would be to fetch replies inside the `hybrid_search` SQL function itself using a lateral join. This eliminates the second round-trip entirely. However, it changes the SQL function signature and return type, which is more invasive.

Recommend starting with the Python-level batch query — simpler, already a ~5x improvement, and doesn't require a SQL migration.

### Expected Impact

- **Before**: 5 sequential queries → ~1-2.5 seconds for replies alone
- **After**: 1 batch query → ~200-400ms total
- Net savings: ~1-2 seconds per request

## Files to Change

- `src/services/message_search/search_messages_hybrid.py` — replace the for-loop with batch query

## Implementation Checklist

- [ ] Replace per-message reply loop with single `in_()` batch query
- [ ] Group replies by `reply_to_message_id`
- [ ] Build enhanced_results in same order as before
- [ ] Test: verify replies are still correctly associated with parent messages
- [ ] Benchmark: compare response times before and after
- [ ] Verify fallback to semantic-only search still works
- [ ] Validate reply fetching behavior against Supabase data before merge

## Status

Planned
