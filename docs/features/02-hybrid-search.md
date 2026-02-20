# Feature: Hybrid Search (Vector + Full-Text)

## Overview

Combine vector similarity search with PostgreSQL full-text search (BM25-style) to improve retrieval accuracy. This addresses the weaknesses of pure vector search, especially for exact keyword matches and rare terms.

## Problem Statement

Pure vector search has known limitations:

1. **Exact keyword misses**: Searching for "PostgreSQL" might return "MySQL" results because they're semantically similar
2. **Rare terms**: Proper nouns, course codes, document numbers don't embed well
3. **Semantic drift**: Vector search can return "similar but wrong" results

**Example failures:**

- Query: "Form A-12" → Vector search might return results about "Form B-15" (similar concept)
- Query: "Professor Rossi" → Might return results about other professors
- Query: "ERASMUS+" → Might miss exact matches due to special characters

## Solution

Implement hybrid search that combines:

1. **Vector search**: Semantic similarity using embeddings
2. **Full-text search**: PostgreSQL `tsvector` for keyword matching
3. **Reciprocal Rank Fusion (RRF)**: Combine scores from both methods

## Technical Design

### Database Schema Changes

Add full-text search column to messages table:

```sql
-- Add tsvector column for full-text search
ALTER TABLE messages ADD COLUMN text_search tsvector;

-- Populate the column
UPDATE messages SET text_search = to_tsvector('simple', text);

-- Create GIN index for fast full-text search
CREATE INDEX messages_text_search_idx ON messages USING GIN (text_search);

-- Create trigger to auto-update on insert/update
CREATE OR REPLACE FUNCTION messages_text_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.text_search := to_tsvector('simple', COALESCE(NEW.text, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER messages_text_search_update
    BEFORE INSERT OR UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION messages_text_search_trigger();
```

### Hybrid Search Function

Create a Supabase function that combines both search methods:

```sql
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int DEFAULT 10,
    full_text_weight float DEFAULT 0.5,
    semantic_weight float DEFAULT 0.5,
    rrf_k int DEFAULT 60
)
RETURNS TABLE (
    id int,
    text text,
    link text,
    reply_to_message_id int,
    semantic_similarity float,
    full_text_rank float,
    combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH semantic_search AS (
        SELECT
            m.id,
            m.text,
            m.link,
            m.reply_to_message_id,
            1 - (m.embedding <=> query_embedding) as similarity,
            ROW_NUMBER() OVER (ORDER BY m.embedding <=> query_embedding) as rank
        FROM messages m
        ORDER BY m.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    full_text_search AS (
        SELECT
            m.id,
            m.text,
            m.link,
            m.reply_to_message_id,
            ts_rank_cd(m.text_search, websearch_to_tsquery('simple', query_text)) as rank_score,
            ROW_NUMBER() OVER (
                ORDER BY ts_rank_cd(m.text_search, websearch_to_tsquery('simple', query_text)) DESC
            ) as rank
        FROM messages m
        WHERE m.text_search @@ websearch_to_tsquery('simple', query_text)
        ORDER BY rank_score DESC
        LIMIT match_count * 2
    ),
    -- Reciprocal Rank Fusion
    combined AS (
        SELECT
            COALESCE(ss.id, fts.id) as id,
            COALESCE(ss.text, fts.text) as text,
            COALESCE(ss.link, fts.link) as link,
            COALESCE(ss.reply_to_message_id, fts.reply_to_message_id) as reply_to_message_id,
            COALESCE(ss.similarity, 0) as semantic_similarity,
            COALESCE(fts.rank_score, 0) as full_text_rank,
            -- RRF score calculation
            COALESCE(semantic_weight / (rrf_k + ss.rank), 0) +
            COALESCE(full_text_weight / (rrf_k + fts.rank), 0) as combined_score
        FROM semantic_search ss
        FULL OUTER JOIN full_text_search fts ON ss.id = fts.id
    )
    SELECT
        c.id,
        c.text,
        c.link,
        c.reply_to_message_id,
        c.semantic_similarity,
        c.full_text_rank,
        c.combined_score
    FROM combined c
    ORDER BY c.combined_score DESC
    LIMIT match_count;
END;
$$;
```

### Code Changes

#### 1. Update Message Search Service

Modify `src/services/message_search.py`:

```python
from typing import Dict, List, Tuple

def search_messages_hybrid(
    query: str,
    count: int = 5,
    semantic_weight: float = 0.5,
    full_text_weight: float = 0.5
) -> Tuple[List[MessageDict], List[float]]:
    """
    Hybrid search combining vector similarity and full-text search.

    Args:
        query: User's search query
        count: Number of results to return
        semantic_weight: Weight for semantic search (0-1)
        full_text_weight: Weight for full-text search (0-1)

    Returns:
        Tuple of (results list, query embedding)
    """

    # Generate embedding for semantic search
    query_embedding = get_embedding(query)

    try:
        # Call hybrid search function
        resp = supabase.rpc(
            "hybrid_search",
            {
                "query_text": query,
                "query_embedding": query_embedding,
                "match_count": count,
                "semantic_weight": semantic_weight,
                "full_text_weight": full_text_weight
            }
        ).execute()

        results = resp.data

        # Log search diagnostics
        for r in results:
            print(f"  ID {r['id']}: semantic={r['semantic_similarity']:.3f}, "
                  f"fulltext={r['full_text_rank']:.3f}, combined={r['combined_score']:.3f}")

        # Convert to MessageDict format
        messages: List[MessageDict] = []
        for r in results:
            messages.append({
                "id": r["id"],
                "text": r["text"],
                "link": r["link"],
                "reply_to_message_id": r["reply_to_message_id"],
                "similarity": r["combined_score"],  # Use combined score
                "semantic_similarity": r["semantic_similarity"],
                "full_text_rank": r["full_text_rank"]
            })

        return messages, query_embedding

    except Exception as e:
        print(f"Error in hybrid search: {e}")
        # Fallback to pure semantic search
        return search_messages_semantic_only(query, count)


def search_messages_semantic_only(query: str, count: int = 5) -> Tuple[List[MessageDict], List[float]]:
    """Fallback to pure semantic search."""
    query_embedding = get_embedding(query)

    resp = supabase.rpc(
        "match_messages",
        {"query_embedding": query_embedding, "match_count": count}
    ).execute()

    return resp.data, query_embedding
```

#### 2. Add Query Preprocessing

Add keyword extraction for better full-text matching:

```python
def preprocess_query_for_fulltext(query: str) -> str:
    """
    Preprocess query for full-text search.
    - Preserve important terms (course codes, names, etc.)
    - Handle special characters
    """
    import re

    # Preserve patterns like "A-12", "ERASMUS+", course codes
    preserved_patterns = []

    # Find and preserve alphanumeric codes (e.g., "A-12", "B2", "ECTS")
    codes = re.findall(r'\b[A-Z]+[-]?\d+\b|\b\d+[-]?[A-Z]+\b', query, re.IGNORECASE)
    preserved_patterns.extend(codes)

    # Find and preserve quoted phrases
    quoted = re.findall(r'"([^"]+)"', query)
    preserved_patterns.extend(quoted)

    # Build search query
    # For PostgreSQL websearch_to_tsquery, we can use:
    # - "word" for exact match
    # - word for stemmed match
    # - word1 OR word2 for alternatives

    return query  # websearch_to_tsquery handles most cases well
```

#### 3. Dynamic Weight Adjustment

Add logic to adjust weights based on query characteristics:

```python
def get_search_weights(query: str) -> Tuple[float, float]:
    """
    Dynamically adjust search weights based on query characteristics.

    Returns:
        Tuple of (semantic_weight, full_text_weight)
    """
    import re

    # Default balanced weights
    semantic_weight = 0.5
    full_text_weight = 0.5

    # Boost full-text for queries with:
    # - Specific codes/numbers
    # - Proper nouns (capitalized words)
    # - Short queries (likely keyword searches)

    has_codes = bool(re.search(r'\b[A-Z]+[-]?\d+\b|\b\d+[-]?[A-Z]+\b', query))
    has_proper_nouns = bool(re.search(r'\b[A-Z][a-z]+\b', query))
    is_short = len(query.split()) <= 3

    if has_codes:
        full_text_weight = 0.7
        semantic_weight = 0.3
    elif is_short and has_proper_nouns:
        full_text_weight = 0.6
        semantic_weight = 0.4

    # Boost semantic for:
    # - Long, descriptive queries
    # - Questions (how, what, why, etc.)

    is_question = query.lower().startswith(('how', 'what', 'why', 'when', 'where', 'who', 'как', 'что', 'почему', 'когда', 'где', 'кто'))
    is_long = len(query.split()) > 6

    if is_question or is_long:
        semantic_weight = 0.6
        full_text_weight = 0.4

    print(f"🔍 Query weights: semantic={semantic_weight}, fulltext={full_text_weight}")
    return semantic_weight, full_text_weight
```

### Updated Search Flow

```python
def search_messages(query: str, count: int = 5) -> Tuple[List[MessageDict], List[float]]:
    """Main search function using hybrid approach."""

    # Get dynamic weights based on query
    semantic_weight, full_text_weight = get_search_weights(query)

    # Perform hybrid search
    results, query_embedding = search_messages_hybrid(
        query=query,
        count=count,
        semantic_weight=semantic_weight,
        full_text_weight=full_text_weight
    )

    # Filter by minimum score threshold
    filtered_results = [r for r in results if r.get("similarity", 0) >= 0.1]

    # Fetch replies for top results
    enhanced_results = fetch_replies_for_results(filtered_results)

    return enhanced_results, query_embedding
```

## Migration Strategy

### Step 1: Add Full-Text Column

```sql
-- Run in Supabase SQL editor
ALTER TABLE messages ADD COLUMN IF NOT EXISTS text_search tsvector;
UPDATE messages SET text_search = to_tsvector('simple', text);
CREATE INDEX IF NOT EXISTS messages_text_search_idx ON messages USING GIN (text_search);
```

### Step 2: Add Trigger

```sql
-- Ensure new messages get text_search populated
CREATE OR REPLACE FUNCTION messages_text_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.text_search := to_tsvector('simple', COALESCE(NEW.text, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS messages_text_search_update ON messages;
CREATE TRIGGER messages_text_search_update
    BEFORE INSERT OR UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION messages_text_search_trigger();
```

### Step 3: Create Hybrid Search Function

Deploy the `hybrid_search` function to Supabase.

### Step 4: Update Application Code

Deploy updated `message_search.py` with hybrid search support.

## Configuration Options

Add to `src/config/settings.py`:

```python
# Hybrid search configuration
HYBRID_SEARCH_ENABLED = True
DEFAULT_SEMANTIC_WEIGHT = 0.5
DEFAULT_FULLTEXT_WEIGHT = 0.5
MIN_RESULT_SCORE = 0.1
RRF_K = 60  # Reciprocal Rank Fusion constant
```

## Performance Considerations

1. **Index Size**: GIN index adds ~10-20% to table size
2. **Query Time**: Full-text search is fast with GIN index (~1-5ms)
3. **Combined Overhead**: Hybrid search ~2x single method (still <100ms)

## Success Metrics

1. **Exact Match Rate**: Percentage of queries with exact keyword matches in top results
2. **Retrieval Precision**: Manual evaluation of result relevance
3. **Query Latency**: P50/P95 response times

## Implementation Checklist

- [ ] Add `text_search` column to messages table
- [ ] Create GIN index on `text_search`
- [ ] Add trigger for auto-populating `text_search`
- [ ] Create `hybrid_search` Supabase function
- [ ] Implement `search_messages_hybrid()` in Python
- [ ] Add dynamic weight calculation
- [ ] Add configuration options
- [ ] Test with various query types
- [ ] Measure performance impact
- [ ] A/B test against pure vector search
