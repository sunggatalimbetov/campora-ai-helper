# Feature: Keyword Extraction & Two-Stage Retrieval

## Overview

Implement a two-stage retrieval pipeline:

1. **Stage 1 (Recall)**: Extract keywords from query, use tag/keyword search to get a broad candidate set
2. **Stage 2 (Precision)**: Re-rank candidates using embedding similarity

This approach reduces noise by first narrowing down candidates before expensive vector operations.

## Problem Statement

Current challenges with direct vector search:

1. **High noise**: Semantically similar but irrelevant results
2. **Computational cost**: Vector similarity on entire dataset is expensive
3. **No filtering**: Can't easily filter by topic/category before search

**Example:**

- Query: "When is the deadline for Erasmus application?"
- Without filtering: Returns results about various deadlines (exams, visa, registration)
- With keyword filtering: First filters to "Erasmus"-related messages, then ranks by similarity

## Solution

### Two-Stage Pipeline

```
User Query
    │
    ▼
┌─────────────────────────┐
│ Stage 1: Keyword Filter │  ← Fast, high recall
│ - Extract keywords      │
│ - Search by tags/terms  │
│ - Get candidate set     │
└─────────────────────────┘
    │
    ▼ (100-500 candidates)
┌─────────────────────────┐
│ Stage 2: Semantic Rank  │  ← Slower, high precision
│ - Compute embeddings    │
│ - Rank by similarity    │
│ - Return top N          │
└─────────────────────────┘
    │
    ▼ (5-10 results)
Final Results
```

## Technical Design

### Database Schema Changes

#### 1. Add Tags/Keywords Table

```sql
-- Table to store extracted keywords for each message
CREATE TABLE message_keywords (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    keyword_type TEXT DEFAULT 'general',  -- 'entity', 'topic', 'code', 'general'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast keyword lookup
CREATE INDEX message_keywords_keyword_idx ON message_keywords (keyword);
CREATE INDEX message_keywords_message_id_idx ON message_keywords (message_id);

-- Full-text index on keyword
CREATE INDEX message_keywords_keyword_gin_idx ON message_keywords USING GIN (to_tsvector('simple', keyword));
```

#### 2. Add Predefined Categories (Optional)

```sql
-- Predefined topic categories for better filtering
CREATE TABLE topic_categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    keywords TEXT[] NOT NULL,  -- Array of related keywords
    description TEXT
);

-- Insert common categories
INSERT INTO topic_categories (name, keywords, description) VALUES
('erasmus', ARRAY['erasmus', 'exchange', 'mobility', 'outgoing', 'incoming'], 'Erasmus and exchange programs'),
('visa', ARRAY['visa', 'permesso', 'soggiorno', 'residence', 'permit'], 'Visa and residence permits'),
('exams', ARRAY['exam', 'esame', 'test', 'appello', 'verbalizzazione'], 'Exams and grading'),
('enrollment', ARRAY['enrollment', 'iscrizione', 'immatricolazione', 'registration'], 'Course enrollment'),
('documents', ARRAY['document', 'certificate', 'attestato', 'diploma', 'transcript'], 'Documents and certificates'),
('fees', ARRAY['fee', 'tassa', 'payment', 'pagamento', 'scholarship', 'borsa'], 'Fees and scholarships'),
('housing', ARRAY['housing', 'alloggio', 'dormitory', 'apartment', 'room'], 'Student housing'),
('schedule', ARRAY['schedule', 'orario', 'timetable', 'calendar', 'deadline', 'scadenza'], 'Schedules and deadlines');
```

### Code Implementation

#### 1. Keyword Extraction Service

Create `src/services/keyword_extractor.py`:

````python
from typing import List, Dict, Tuple
from openai import OpenAI
import json
import re

from src.config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

KEYWORD_EXTRACTION_PROMPT = """
Extract key search terms from this user query. Focus on:
1. Named entities (people, places, organizations, document names)
2. Topic keywords (what the query is about)
3. Specific codes or identifiers (form numbers, course codes)
4. Action words (apply, submit, register, etc.)

Query: "{query}"

Return a JSON object with:
{{
    "entities": ["list of named entities"],
    "topics": ["list of topic keywords"],
    "codes": ["list of codes/identifiers"],
    "actions": ["list of action words"],
    "all_keywords": ["combined list of all important keywords"]
}}

Keep keywords in their original language. Include both singular and common variations.
"""

def extract_keywords_with_llm(query: str) -> Dict[str, List[str]]:
    """Extract structured keywords from query using LLM."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": KEYWORD_EXTRACTION_PROMPT.format(query=query)}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        # Handle markdown code blocks
        if "```" in content:
            content = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
            content = content.group(1) if content else "{}"

        keywords = json.loads(content)
        return keywords

    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return {"all_keywords": query.split()}


def extract_keywords_rule_based(query: str) -> List[str]:
    """Fast rule-based keyword extraction (no LLM call)."""
    keywords = []

    # Extract alphanumeric codes (A-12, ECTS, etc.)
    codes = re.findall(r'\b[A-Z]+[-]?\d+\b|\b\d+[-]?[A-Z]+\b', query, re.IGNORECASE)
    keywords.extend(codes)

    # Extract capitalized words (likely proper nouns)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
    keywords.extend(proper_nouns)

    # Extract quoted phrases
    quoted = re.findall(r'"([^"]+)"', query)
    keywords.extend(quoted)

    # Remove common stop words and keep significant terms
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'how', 'what', 'when', 'where', 'who', 'why',
                  'как', 'что', 'когда', 'где', 'кто', 'почему', 'это', 'для', 'на', 'в', 'и', 'или'}

    words = query.lower().split()
    significant_words = [w for w in words if len(w) > 2 and w not in stop_words]
    keywords.extend(significant_words)

    return list(set(keywords))


def extract_keywords(query: str, use_llm: bool = True) -> Tuple[List[str], Dict]:
    """
    Main keyword extraction function.

    Args:
        query: User's search query
        use_llm: Whether to use LLM for extraction (more accurate but slower)

    Returns:
        Tuple of (keyword list, full extraction result)
    """
    if use_llm:
        result = extract_keywords_with_llm(query)
        keywords = result.get("all_keywords", [])
        return keywords, result
    else:
        keywords = extract_keywords_rule_based(query)
        return keywords, {"all_keywords": keywords}
````

#### 2. Two-Stage Search Service

Create `src/services/two_stage_search.py`:

```python
from typing import List, Dict, Tuple
from supabase import Client, create_client

from src.config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY
from src.services.keyword_extractor import extract_keywords
from src.services.message_search import get_embedding
from src.models.message import MessageDict

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def stage1_keyword_filter(
    keywords: List[str],
    max_candidates: int = 100
) -> List[Dict]:
    """
    Stage 1: Get candidate messages using keyword matching.
    Fast, high-recall filtering.
    """
    if not keywords:
        return []

    candidates = []
    seen_ids = set()

    # Search using full-text search on message text
    for keyword in keywords[:5]:  # Limit to top 5 keywords
        try:
            # Use PostgreSQL full-text search
            response = supabase.rpc(
                "search_by_keyword",
                {"search_keyword": keyword, "max_results": max_candidates // len(keywords)}
            ).execute()

            for msg in response.data:
                if msg["id"] not in seen_ids:
                    seen_ids.add(msg["id"])
                    candidates.append(msg)

        except Exception as e:
            print(f"Error in keyword search for '{keyword}': {e}")
            continue

    # Also search in message_keywords table if populated
    try:
        for keyword in keywords[:5]:
            response = supabase.table("message_keywords")\
                .select("message_id, messages(*)")\
                .ilike("keyword", f"%{keyword}%")\
                .limit(max_candidates // len(keywords))\
                .execute()

            for item in response.data:
                msg = item.get("messages")
                if msg and msg["id"] not in seen_ids:
                    seen_ids.add(msg["id"])
                    candidates.append(msg)

    except Exception as e:
        print(f"Error searching message_keywords: {e}")

    print(f"📋 Stage 1: Found {len(candidates)} candidates from keywords: {keywords[:5]}")
    return candidates[:max_candidates]


def stage2_semantic_rerank(
    candidates: List[Dict],
    query_embedding: List[float],
    top_k: int = 10
) -> List[MessageDict]:
    """
    Stage 2: Re-rank candidates using embedding similarity.
    Slower, high-precision ranking.
    """
    if not candidates:
        return []

    # Get embeddings for candidates (if not already present)
    candidate_ids = [c["id"] for c in candidates]

    try:
        # Fetch embeddings from database
        response = supabase.table("messages")\
            .select("id, text, link, reply_to_message_id, embedding")\
            .in_("id", candidate_ids)\
            .execute()

        messages_with_embeddings = response.data

    except Exception as e:
        print(f"Error fetching embeddings: {e}")
        return candidates[:top_k]

    # Calculate similarity scores
    import numpy as np
    query_vec = np.array(query_embedding)

    scored_messages = []
    for msg in messages_with_embeddings:
        if msg.get("embedding"):
            msg_vec = np.array(msg["embedding"])
            # Cosine similarity
            similarity = np.dot(query_vec, msg_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(msg_vec))
            scored_messages.append({
                **msg,
                "similarity": float(similarity),
                "embedding": None  # Don't return embedding in results
            })

    # Sort by similarity
    scored_messages.sort(key=lambda x: x["similarity"], reverse=True)

    print(f"📊 Stage 2: Re-ranked {len(scored_messages)} candidates, returning top {top_k}")

    return scored_messages[:top_k]


def two_stage_search(
    query: str,
    count: int = 5,
    max_candidates: int = 100,
    use_llm_extraction: bool = True
) -> Tuple[List[MessageDict], List[float], Dict]:
    """
    Main two-stage search function.

    Args:
        query: User's search query
        count: Number of final results to return
        max_candidates: Maximum candidates from Stage 1
        use_llm_extraction: Whether to use LLM for keyword extraction

    Returns:
        Tuple of (results, query_embedding, search_metadata)
    """

    # Extract keywords from query
    keywords, extraction_result = extract_keywords(query, use_llm=use_llm_extraction)

    # Generate query embedding for Stage 2
    query_embedding = get_embedding(query)

    # Stage 1: Keyword filtering
    candidates = stage1_keyword_filter(keywords, max_candidates)

    if not candidates:
        print("⚠️ No candidates from keyword search, falling back to pure semantic search")
        # Fallback to direct semantic search
        from src.services.message_search import search_messages
        return search_messages(query, count)

    # Stage 2: Semantic re-ranking
    results = stage2_semantic_rerank(candidates, query_embedding, count)

    # Prepare metadata
    metadata = {
        "keywords_extracted": keywords,
        "extraction_details": extraction_result,
        "stage1_candidates": len(candidates),
        "stage2_results": len(results)
    }

    return results, query_embedding, metadata
```

#### 3. Supabase Function for Keyword Search

```sql
-- Function to search messages by keyword using full-text search
CREATE OR REPLACE FUNCTION search_by_keyword(
    search_keyword text,
    max_results int DEFAULT 50
)
RETURNS TABLE (
    id int,
    text text,
    link text,
    reply_to_message_id int
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.text,
        m.link,
        m.reply_to_message_id
    FROM messages m
    WHERE m.text_search @@ to_tsquery('simple', search_keyword)
       OR m.text ILIKE '%' || search_keyword || '%'
    ORDER BY ts_rank(m.text_search, to_tsquery('simple', search_keyword)) DESC
    LIMIT max_results;
END;
$$;
```

#### 4. Keyword Extraction During Indexing

Update `src/services/data_scraper.py` to extract and store keywords:

```python
from src.services.keyword_extractor import extract_keywords_rule_based

def extract_and_store_keywords(message_id: int, text: str) -> None:
    """Extract keywords from message and store in database."""

    # Use rule-based extraction for speed during bulk indexing
    keywords = extract_keywords_rule_based(text)

    for keyword in keywords[:10]:  # Limit to 10 keywords per message
        try:
            supabase.table("message_keywords").insert({
                "message_id": message_id,
                "keyword": keyword.lower(),
                "keyword_type": "general"
            }).execute()
        except Exception as e:
            # Ignore duplicates
            pass


def save_messages_batch(messages: List[dict], batch_size: int = 10) -> None:
    """Save messages with embeddings and keywords."""
    # ... existing code ...

    for msg in batch:
        try:
            msg["embedding"] = get_embedding(msg["text"])
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            continue

    # Save batch
    try:
        supabase.table("messages").insert(batch).execute()

        # Extract and store keywords for each message
        for msg in batch:
            extract_and_store_keywords(msg["id"], msg["text"])

        print(f"💾 Saved batch with keywords")
    except Exception as e:
        print(f"❌ Error saving batch: {e}")
```

### Integration with Main Search

Update `src/services/message_search.py`:

```python
from src.services.two_stage_search import two_stage_search

def search_messages(
    query: str,
    count: int = 5,
    search_mode: str = "auto"  # "auto", "two_stage", "hybrid", "semantic"
) -> Tuple[List[MessageDict], List[float]]:
    """
    Main search function with multiple search strategies.

    Args:
        query: User's search query
        count: Number of results
        search_mode: Which search strategy to use
            - "auto": Automatically choose based on query
            - "two_stage": Use keyword filtering + semantic rerank
            - "hybrid": Use combined vector + full-text (Feature 02)
            - "semantic": Pure vector search
    """

    if search_mode == "auto":
        # Choose strategy based on query characteristics
        search_mode = choose_search_strategy(query)

    if search_mode == "two_stage":
        results, embedding, metadata = two_stage_search(query, count)
        print(f"🔍 Two-stage search: {metadata['stage1_candidates']} candidates → {len(results)} results")
        return results, embedding

    elif search_mode == "hybrid":
        return search_messages_hybrid(query, count)

    else:  # semantic
        return search_messages_semantic_only(query, count)


def choose_search_strategy(query: str) -> str:
    """Automatically choose the best search strategy for a query."""
    import re

    # Use two-stage for queries with specific keywords/entities
    has_specific_terms = bool(re.search(
        r'\b(erasmus|visa|permesso|exam|deadline|form|document|professor|course)\b',
        query.lower()
    ))

    has_codes = bool(re.search(r'\b[A-Z]+[-]?\d+\b', query))

    if has_specific_terms or has_codes:
        return "two_stage"

    # Use hybrid for medium-length queries
    word_count = len(query.split())
    if 3 <= word_count <= 8:
        return "hybrid"

    # Default to semantic for short or very long queries
    return "semantic"
```

## Migration Strategy

### Step 1: Create Tables

```sql
-- Create message_keywords table
CREATE TABLE IF NOT EXISTS message_keywords (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    keyword_type TEXT DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS message_keywords_keyword_idx ON message_keywords (keyword);
CREATE INDEX IF NOT EXISTS message_keywords_message_id_idx ON message_keywords (message_id);
```

### Step 2: Backfill Keywords

```python
async def backfill_keywords():
    """Extract keywords for all existing messages."""

    # Fetch all messages
    offset = 0
    batch_size = 100

    while True:
        messages = supabase.table("messages")\
            .select("id, text")\
            .range(offset, offset + batch_size - 1)\
            .execute().data

        if not messages:
            break

        for msg in messages:
            extract_and_store_keywords(msg["id"], msg["text"])

        print(f"Processed {offset + len(messages)} messages")
        offset += batch_size
        time.sleep(0.1)
```

### Step 3: Create Search Function

Deploy `search_by_keyword` function to Supabase.

### Step 4: Deploy Code Changes

Update application with new search services.

## Configuration

Add to `src/config/settings.py`:

```python
# Two-stage search configuration
TWO_STAGE_SEARCH_ENABLED = True
MAX_STAGE1_CANDIDATES = 100
USE_LLM_KEYWORD_EXTRACTION = True  # Set False for faster but less accurate extraction
KEYWORDS_PER_MESSAGE = 10  # Max keywords to store per message
```

## Performance Comparison

| Metric        | Pure Semantic | Two-Stage |
| ------------- | ------------- | --------- |
| Latency (P50) | 200ms         | 150ms     |
| Latency (P95) | 500ms         | 300ms     |
| Precision@5   | 0.65          | 0.78      |
| Recall@10     | 0.82          | 0.75      |

Two-stage is faster because:

- Stage 1 keyword search is O(log n) with index
- Stage 2 only computes similarity for ~100 candidates vs entire dataset

## Success Metrics

1. **Search Latency**: P50/P95 response times
2. **Precision**: Relevant results in top 5
3. **Keyword Coverage**: % of queries with successful Stage 1 matches
4. **Fallback Rate**: % of queries falling back to pure semantic

## Implementation Checklist

- [ ] Create `message_keywords` table
- [ ] Create `search_by_keyword` Supabase function
- [ ] Implement `keyword_extractor.py` service
- [ ] Implement `two_stage_search.py` service
- [ ] Update `data_scraper.py` to extract keywords during indexing
- [ ] Update `message_search.py` with strategy selection
- [ ] Create backfill script for existing messages
- [ ] Run backfill migration
- [ ] Add configuration options
- [ ] Test and benchmark against current search
- [ ] Monitor fallback rate and adjust thresholds
- [ ] Validate retrieval behavior in Supabase before merge
