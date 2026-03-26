# Feature: Question Generation for Improved Retrieval

## Overview

Generate hypothetical questions for each indexed message and store their embeddings alongside the original message embeddings. This bridges the semantic gap between user queries (questions) and indexed content (answers/statements).

## Problem Statement

Currently, when users ask questions, we search for semantically similar content. However:

- User queries are typically phrased as **questions**
- Indexed messages are typically **statements or answers**
- This creates a semantic mismatch that reduces retrieval quality

**Example:**

- User query: "How do I apply for Erasmus?"
- Indexed message: "You need to submit form A-12 to the international office by March 15th"
- These are semantically related but phrased very differently

## Solution

During indexing, use an LLM to generate 2-3 hypothetical questions that each message could answer. Store embeddings for both:

1. The original message text
2. The generated questions

At search time, the user's question will have higher similarity to our generated questions.

## Technical Design

### Database Schema Changes

Add a new table `message_questions` to store generated questions:

```sql
CREATE TABLE message_questions (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX message_questions_embedding_idx
ON message_questions
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### New Supabase Function

Create a function to search both messages and questions:

```sql
CREATE OR REPLACE FUNCTION match_messages_and_questions(
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    message_id int,
    text text,
    link text,
    similarity float,
    match_source text  -- 'message' or 'question'
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH message_matches AS (
        SELECT
            m.id as message_id,
            m.text,
            m.link,
            1 - (m.embedding <=> query_embedding) as similarity,
            'message'::text as match_source
        FROM messages m
        ORDER BY m.embedding <=> query_embedding
        LIMIT match_count
    ),
    question_matches AS (
        SELECT
            mq.message_id,
            m.text,
            m.link,
            1 - (mq.embedding <=> query_embedding) as similarity,
            'question'::text as match_source
        FROM message_questions mq
        JOIN messages m ON m.id = mq.message_id
        ORDER BY mq.embedding <=> query_embedding
        LIMIT match_count
    ),
    combined AS (
        SELECT * FROM message_matches
        UNION ALL
        SELECT * FROM question_matches
    )
    SELECT DISTINCT ON (c.message_id)
        c.message_id,
        c.text,
        c.link,
        MAX(c.similarity) as similarity,
        c.match_source
    FROM combined c
    GROUP BY c.message_id, c.text, c.link, c.match_source
    ORDER BY c.message_id, MAX(c.similarity) DESC
    LIMIT match_count;
END;
$$;
```

### Code Changes

#### 1. New Question Generator Service

Create `src/services/question_generator.py`:

```python
from typing import List
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

QUESTION_GENERATION_PROMPT = """
Analyze this message from a university student group chat and generate 2-3 questions that this message could be answering.

Message: "{message_text}"

Rules:
- Generate questions that a student might naturally ask
- Questions should be in the same language as the message
- Focus on the key information in the message
- If the message is already a question, generate similar alternative phrasings
- If the message contains no useful information, return an empty list

Return ONLY a JSON array of questions, like:
["Question 1?", "Question 2?", "Question 3?"]

If no good questions can be generated, return: []
"""

def generate_questions_for_message(message_text: str) -> List[str]:
    """Generate hypothetical questions that this message could answer."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": QUESTION_GENERATION_PROMPT.format(message_text=message_text[:1000])}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        # Parse JSON response
        import json
        questions = json.loads(content)
        return questions if isinstance(questions, list) else []

    except Exception as e:
        print(f"Error generating questions: {e}")
        return []
```

#### 2. Update Data Scraper

Modify `src/services/data_scraper.py` to generate and store questions during indexing:

```python
from src.services.question_generator import generate_questions_for_message

def save_messages_batch(messages: List[dict], batch_size: int = 10) -> None:
    """Save messages in batches with embeddings and generated questions."""
    total = len(messages)

    for i in range(0, total, batch_size):
        batch = messages[i : i + batch_size]

        for msg in batch:
            try:
                # Generate embedding for original message
                msg["embedding"] = get_embedding(msg["text"])

                # Generate questions and their embeddings
                questions = generate_questions_for_message(msg["text"])
                msg["_generated_questions"] = []

                for q in questions:
                    q_embedding = get_embedding(q)
                    msg["_generated_questions"].append({
                        "question_text": q,
                        "embedding": q_embedding
                    })

            except Exception as e:
                print(f"❌ Error processing message {msg['id']}: {e}")
                continue

        # Save messages to database
        try:
            for msg in batch:
                questions = msg.pop("_generated_questions", [])

                # Insert message
                supabase.table("messages").insert(msg).execute()

                # Insert generated questions
                for q in questions:
                    supabase.table("message_questions").insert({
                        "message_id": msg["id"],
                        "question_text": q["question_text"],
                        "embedding": q["embedding"]
                    }).execute()

            print(f"💾 Saved batch {i//batch_size + 1}")
        except Exception as e:
            print(f"❌ Error saving batch: {e}")

        time.sleep(1)
```

#### 3. Update Search Service

Modify `src/services/message_search.py` to use the new combined search:

```python
def search_messages(query: str, count: int = 5) -> tuple[List[MessageDict], List[float]]:
    """Search using both message and question embeddings."""

    query_embedding = get_embedding(query)

    try:
        # Use new combined search function
        resp = supabase.rpc(
            "match_messages_and_questions",
            {"query_embedding": query_embedding, "match_count": count * 2}
        ).execute()

        results = resp.data
        # ... rest of processing

    except Exception as e:
        print(f"Error in search: {e}")
        # Fallback to original search
```

## Migration Strategy

### For Existing Messages

Create a migration script to generate questions for existing messages:

```python
async def backfill_questions():
    """Generate questions for all existing messages."""

    # Fetch messages without questions
    messages = supabase.table("messages").select("id, text").execute().data

    for msg in messages:
        # Check if questions already exist
        existing = supabase.table("message_questions")\
            .select("id")\
            .eq("message_id", msg["id"])\
            .execute()

        if existing.data:
            continue

        # Generate and save questions
        questions = generate_questions_for_message(msg["text"])
        for q in questions:
            embedding = get_embedding(q)
            supabase.table("message_questions").insert({
                "message_id": msg["id"],
                "question_text": q,
                "embedding": embedding
            }).execute()

        time.sleep(0.5)  # Rate limiting
```

## Cost Estimation

For each message:

- 1 LLM call for question generation (~100-200 tokens)
- 2-3 embedding calls for generated questions

**Per 1000 messages:**

- Question generation: ~$0.015 (gpt-4o-mini)
- Embeddings: ~$0.006 (text-embedding-3-small, ~3 questions × 1000)
- **Total: ~$0.02 per 1000 messages**

## Success Metrics

1. **Retrieval Quality**: Measure average similarity scores before/after
2. **User Satisfaction**: Track feedback ratings on search results
3. **Coverage**: Percentage of queries that return results above threshold

## Implementation Checklist

- [ ] Create `message_questions` table in Supabase
- [ ] Create `match_messages_and_questions` function
- [ ] Implement `question_generator.py` service
- [ ] Update `data_scraper.py` to generate questions during indexing
- [ ] Update `message_search.py` to use combined search
- [ ] Create backfill migration script
- [ ] Run backfill on existing messages
- [ ] Test and measure improvement
- [ ] Validate the new table/function behavior in Supabase before merge
