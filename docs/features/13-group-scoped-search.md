# Feature: Group-Scoped Search

## Problem

Currently, `search_messages_hybrid` searches across ALL groups in the `messages` table. When a user asks a question in Group A, they may get results from Group B — which is confusing and often irrelevant.

## Solution

When a query originates from a group chat, scope the search to that group's `chat_id`. In DMs, continue searching across all groups (the user isn't in a specific group context).

## Technical Design

### Database Changes

The `hybrid_search` SQL function needs a new optional `filter_chat_id` parameter:

```sql
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    semantic_weight float DEFAULT 0.5,
    full_text_weight float DEFAULT 0.5,
    rrf_k int DEFAULT 60,
    filter_chat_id bigint DEFAULT NULL  -- NEW: optional chat_id filter
)
RETURNS TABLE (...)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Add WHERE clause when filter_chat_id is provided:
    -- WHERE (filter_chat_id IS NULL OR m.chat_id = filter_chat_id)
    ...
END;
$$;
```

### Python Changes

#### 1. Update `search_messages_hybrid.py`

Add `chat_id` parameter:

```python
def search_messages_hybrid(
    query: str,
    count: int = 5,
    semantic_weight: float = 0.5,
    full_text_weight: float = 0.5,
    chat_id: int | None = None,  # NEW
) -> Tuple[List[MessageDict], List[float]]:

    # Pass to RPC:
    params = {
        "query_text": fulltext_query,
        "query_embedding": query_embedding,
        "match_count": count,
        "semantic_weight": semantic_weight,
        "full_text_weight": full_text_weight,
        "rrf_k": RRF_K,
    }
    if chat_id is not None:
        params["filter_chat_id"] = chat_id

    resp = supabase.rpc("hybrid_search", params).execute()
```

#### 2. Update `search_messages` wrapper

In `src/services/message_search/__init__.py`, pass `chat_id` through:

```python
def search_messages(query, count=5, chat_id=None):
    return search_messages_hybrid(query, count, chat_id=chat_id)
```

#### 3. Update handlers

In `ask_command` (group context):
```python
results, query_embedding = search_messages(search_query, chat_id=chat_id)
```

In `dm_handler` (no scoping):
```python
results, query_embedding = search_messages(search_query)  # searches all groups
```

### DM Behavior — Future Enhancement

Later, we could let DM users specify which group to search with `/ask -g <group_name> <question>`, or auto-detect based on which groups the user belongs to. Out of scope for this feature.

### Fallback Strategy

If group-scoped search returns 0 results, optionally fall back to global search with a note: "Не нашёл в этой группе, но вот что нашёл в других:"

This is optional and can be added later based on user feedback.

## Files to Change

- `sql/` — new migration to update `hybrid_search` function with `filter_chat_id` param
- `src/services/message_search/search_messages_hybrid.py` — add `chat_id` parameter
- `src/services/message_search/__init__.py` — pass `chat_id` through
- `src/handlers/commands.py` — pass `chat_id` in `ask_command`

## Implementation Checklist

- [ ] Write SQL migration to add `filter_chat_id` param to `hybrid_search` function
- [ ] Deploy migration to Supabase
- [ ] Add `chat_id` parameter to `search_messages_hybrid()`
- [ ] Update `search_messages()` wrapper to accept and pass `chat_id`
- [ ] Update `ask_command` to pass `chat_id` for group queries
- [ ] Verify DM search still works across all groups (no `chat_id` passed)
- [ ] Test: ask in Group A → results only from Group A
- [ ] Test: ask in DM → results from all groups
- [ ] Validate the RPC behavior in Supabase before merge

## Status

Planned
