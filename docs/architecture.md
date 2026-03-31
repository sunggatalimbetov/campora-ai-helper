# Architecture Explanations

Deep dives into how the major systems in campora-ai-helper work and why they're built the way they are.

---

## 1. The Campora AI Ecosystem

```
[Telegram Groups]
      │ scrapes messages
      ▼
campora-ai-scraper          Supabase (PostgreSQL + pgvector)
(Telethon userbot)  ──────► messages table (text + embeddings)
                            message_questions table (hypothetical Q embeddings)
                            bot_interactions table (usage logs)
                            user_preferences table
                            opted_out_users table
                                │
                                │ reads
                                ▼
                        campora-ai-helper (this repo)
                        (python-telegram-bot)
                                │
                                │ answers
                                ▼
                        [Students in Telegram DMs / Groups]

                        campora-ai-dashboard
                        (analytics & monitoring)
                                │ reads
                                ▼
                        bot_interactions table
```

**The scraper** runs as a Telethon userbot, joining university group chats and storing messages with their OpenAI embeddings into Supabase. It also generates hypothetical questions for each message and stores those embeddings separately.

**The helper** (this repo) is the user-facing Telegram bot. Students ask questions via DM or `/ask` in groups. The bot searches scraped messages using hybrid vector + full-text search, then generates answers with GPT-4o-mini.

**The dashboard** reads from the `bot_interactions` table for usage analytics, feedback tracking, and search quality monitoring.

---

## 2. The Hybrid Search Pipeline

This is the core of the bot — how it finds relevant messages to answer a question.

### Overview

```
User query
  │
  ├─ 1. Rewrite query (if conversation history exists)
  ├─ 2. Generate embedding (text-embedding-3-small, 1536 dims)
  ├─ 3. Run hybrid search (vector + Russian full-text + RRF)
  ├─ 4. Run question-embedding search (supplementary)
  ├─ 5. Merge and deduplicate results
  ├─ 6. Attach reply threads
  └─ 7. Filter by minimum score
```

### Step 1: Query Rewriting

When the user has conversation history (previous Q&A in the same session), the raw query might be ambiguous — "what about the second one?" doesn't make sense without context. `rewrite_query()` sends the last 3 turns + the new query to GPT-4o-mini with instructions to produce a standalone search query. If there's no history, the query passes through unchanged.

### Step 2: Embedding Generation

The rewritten query is embedded using OpenAI's `text-embedding-3-small` model (1536 dimensions). This same model was used by the scraper to embed messages, so the vectors are in the same space.

### Step 3: Hybrid Search

This is where it gets interesting. The search combines two approaches:

**Vector (semantic) search** finds messages whose meaning is similar, even if the words differ. "When are finals?" matches "exam schedule is posted on the board."

**Full-text search** finds messages containing the exact terms, using PostgreSQL's `tsvector` with Russian language support. "IELTS 7.0" matches "you need IELTS 7.0 minimum."

Neither approach alone is sufficient — semantic search misses exact codes/names, full-text misses paraphrases. The hybrid approach combines both using **Reciprocal Rank Fusion (RRF)**.

#### Why RRF instead of simple score blending?

Semantic similarity scores (0–1) and full-text rank scores (arbitrary floats) are on completely different scales. Simply averaging them would let one dominate. RRF solves this by converting both to rank-based scores:

```
RRF_score = semantic_weight / (K + semantic_rank) + fulltext_weight / (K + fulltext_rank)
```

Where `K=60` is a smoothing constant. This makes the combination rank-based rather than score-based, giving both signals fair influence regardless of their raw score magnitudes.

#### Dynamic weight adjustment

Not all queries benefit equally from both approaches. The weights are adjusted based on query characteristics:

| Query Type | Semantic | Fulltext | Why |
|------------|----------|----------|-----|
| Contains codes (e.g., "CS-101") | 0.3 | 0.7 | Exact term matching needed |
| Short + proper nouns (e.g., "Dean Smith") | 0.4 | 0.6 | Names need exact match |
| Question or long query (>6 words) | 0.6 | 0.4 | Intent understanding needed |
| Default | 0.5 | 0.5 | Balanced |

#### Full-text term extraction

Before passing the query to PostgreSQL's `websearch_to_tsquery`, Russian and English stop words are stripped (~90 Russian, ~20 English). This prevents common words like "как", "что", "можно" from dominating the full-text ranking. Course codes with hyphens (like "A-12") are preserved.

### Step 4: Question-Embedding Search

The scraper generates hypothetical questions for each message. For example, a message saying "2+2=4" might have a generated question "what is basic arithmetic?". These question embeddings are stored in the `message_questions` table.

This supplementary search finds messages by matching against these hypothetical questions, catching cases where the message text itself doesn't semantically match the query but the implicit topic does.

### Step 5: Merge and Deduplicate

Hybrid results and question results are merged:
- Deduplicated by `(message_id, chat_id)` — keeps the entry with higher similarity
- New messages from question search are added if not already present
- Reply entries from hybrid results are preserved as-is

### Step 6: Reply Attachment

Messages in Telegram groups are often Q&A threads — someone asks a question, others reply with answers. The replies contain the actual useful information.

After the main search, replies to all found messages are fetched in a single batch query. Each reply is tagged with `is_reply: True` and `replying_to: parent_id`, inheriting the parent's similarity score. This gives the LLM the full thread context.

### Step 7: Score Filtering

Results below `MIN_RESULT_SCORE` (0.1) are dropped. This is a separate, lower threshold than `SIMILARITY_THRESHOLD` (0.45) which filters within the hybrid search itself. The two-tier approach keeps moderately relevant results from question search while filtering truly irrelevant noise.

### Database RPCs

Three PostgreSQL functions power the search, all supporting `filter_chat_ids BIGINT[]` for multi-group scoping:

| RPC | Purpose |
|-----|---------|
| `match_messages` | Pure vector search (fallback) |
| `hybrid_search` | Vector + full-text with RRF |
| `match_messages_and_questions` | Searches both message and question embeddings, deduplicates by message_id |

---

## 3. Conversation Memory and Sessions

### How sessions work

The bot remembers recent conversation turns so users can ask follow-up questions. A session is a group of related interactions, identified by a UUID stored in `bot_interactions.session_id`.

**Session boundaries:**
- **Timeout:** 30 minutes of inactivity starts a fresh session
- **Manual reset:** `/new` command forces a fresh session
- **Scope:** Sessions are per `(user_id, chat_id)` pair — a user's DM session is separate from their group session

### History loading

When a query comes in, `load_conversation_history()` pulls the last 5 successful interactions for that user+chat within the 30-minute window. Each turn is a `ConversationTurn(query, answer, timestamp)`.

### How history affects search

The conversation history is used in two places:

1. **Query rewriting** — GPT-4o-mini rewrites ambiguous follow-ups into standalone queries using the last 3 turns as context. "What about deadlines?" becomes "What are the application deadlines for KBTU?"

2. **Answer generation** — The full history (up to 5 turns) is included in the message array sent to GPT-4o-mini, allowing it to maintain conversational coherence.

### Answer trimming for history

When history turns are included in future prompts, the stored answers are trimmed:
- References section (📎 Sources/Источники/Дереккөздер) is stripped
- Text is capped at 300 characters, truncated at word boundary

This prevents prompt bloat — without trimming, 5 turns of full answers with references could consume most of the context window.

---

## 4. Answer Generation

### The system prompt

The system prompt is carefully crafted with several layers:

1. **Role definition** — "helpful assistant for university students" with a specific topic scope
2. **Topic filter** — Reject off-topic questions before attempting to answer (dating advice, cooking, etc.)
3. **Source interpretation rules** — Never mention "context" or "provided information"; respond naturally
4. **Thread awareness** — Replies contain actual answers; prioritize them
5. **Date awareness** — Cite source dates for time-sensitive topics; caveat if sources >6 months old; never present relative dates from old messages as current facts
6. **Language instruction** — Answer in the user's preferred language

### Group vs. private mode

In group chats, an addendum constrains responses to 2–3 sentences maximum with direct answers only. This prevents the bot from flooding group conversations with long responses. For complex topics, it suggests the user DM the bot instead.

### Decline detection

After generating an answer, `is_declined()` checks for known refusal phrases in Russian, Kazakh, and English. If the LLM declined (off-topic question), references are not appended — there's no point citing sources for a rejection message.

### Two generation paths

| Path | Used by | How it works |
|------|---------|-------------|
| `generate_answer()` | `/ask` in groups | Synchronous. Full response generated, references appended, returned as string. |
| `stream_answer()` | DM handler | Async streaming. Returns question_results + async generator yielding deltas. References built separately after streaming completes. |

Both paths use the same `build_messages()` function to construct identical OpenAI message arrays.

---

## 5. The Streaming Response System

### Why streaming?

In DMs, the bot generates longer answers that can take several seconds. Without streaming, the user stares at a "Searching..." message until the full answer is ready. Streaming shows the answer appearing word-by-word, similar to ChatGPT.

### How StreamingResponder works

`StreamingResponder` is a state machine that manages progressive message editing:

```
Init(searching_msg) → push(delta) → _maybe_flush() → finalize()
```

**Key parameters:**

| Parameter | Value | Why |
|-----------|-------|-----|
| `EDIT_INTERVAL` | 1.5 seconds | Telegram rate limits edits to ~1/sec per chat. 1.5s gives margin. |
| `SAFE_LENGTH` | 3800 characters | Telegram's message limit is 4096. Buffer before splitting. |
| `CURSOR` | ▍ | Visual indicator that the bot is still generating. |

### The flush cycle

1. Deltas arrive from OpenAI streaming and accumulate in a buffer
2. Every 1.5 seconds, the responder edits the message with `buffer + cursor`
3. If the buffer exceeds 3800 characters:
   - The current message is finalized with the first chunk (split at paragraph, then newline, then space, then hard cut)
   - A new message is created as a reply with the remainder + cursor
   - Streaming continues into the new message

### Finalization

When streaming completes:
1. Cursor is removed
2. References are appended (if the answer wasn't declined)
3. Final message is edited with Markdown formatting (falls back to plain text if Markdown parse fails)
4. Feedback keyboard (thumbs up/down) is attached

### Error resilience

- **`RetryAfter`**: Sleeps for the specified duration, then retries the edit
- **`BadRequest`**: Skips the failed edit; accumulated text appears in the next flush
- **Markdown failure**: Falls back to plain text rendering
