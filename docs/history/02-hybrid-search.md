# 02 – Hybrid search (vector + full-text via RRF)

**Date:** 2026-02-14

## Summary

We replaced the old query-expansion-based semantic search with a single-call hybrid search that combines vector similarity and PostgreSQL full-text search using Reciprocal Rank Fusion (RRF). Along the way we fixed a type mismatch that broke the RPC, switched the text-search config from `'simple'` to `'russian'` for proper stemming, and improved the LLM answer prompt.

---

## 1. Hybrid search RPC (`hybrid_search`)

**Problem:** The previous search pipeline generated 3 paraphrased queries via LLM, ran 4 separate `match_messages` calls (original + 3 paraphrases), deduplicated, and sorted. This was slow (4× embedding + 4× RPC), gave no keyword-match capability, and missed exact terms like course codes or proper nouns.

**Solution:** A single `hybrid_search` Supabase function that fuses vector similarity with full-text search in one call.

### SQL function

File: `sql/002_hybrid_search.sql` (mirrored in `supabase/migrations/20260214120000_add_hybrid_search.sql`).

1. **`text_search` column** – `tsvector` column populated by `to_tsvector('russian', text)`, with a GIN index for fast lookup.
2. **Auto-populate trigger** – `messages_text_search_trigger()` runs `BEFORE INSERT OR UPDATE` to keep the column in sync.
3. **`hybrid_search()` RPC** – accepts `query_text`, `query_embedding vector(1536)`, `match_count`, `full_text_weight`, `semantic_weight`, `rrf_k`. Internally:
   - `semantic_search` CTE: orders by `embedding <=> query_embedding`, returns top `match_count * 2` rows with a `rank` column.
   - `full_text_search` CTE: filters by `text_search @@ websearch_to_tsquery('russian', query_text)`, ranks with `ts_rank_cd`, returns top `match_count * 2` rows.
   - `combined` CTE: `FULL OUTER JOIN` on `id`, computes `combined_score = semantic_weight / (rrf_k + semantic_rank) + full_text_weight / (rrf_k + fulltext_rank)`.
   - Final SELECT orders by `combined_score DESC` and limits to `match_count`.

Returns: `id, chat_id, author, text, link, reply_to_message_id, semantic_similarity, full_text_rank, combined_score`.

---

## 2. Python-side changes

### `src/config/settings.py`

Added hybrid-search config constants:

```python
HYBRID_SEARCH_ENABLED = True
DEFAULT_SEMANTIC_WEIGHT = 0.5
DEFAULT_FULLTEXT_WEIGHT = 0.5
MIN_RESULT_SCORE = 0.1      # minimum semantic_similarity to keep a result
RRF_K = 60                  # RRF smoothing constant
```

### `src/services/message_search.py`

Replaced the multi-query expansion pipeline with three functions:

- **`get_search_weights(query)`** – dynamically adjusts `semantic_weight` / `full_text_weight` based on query traits:
  - Codes like `A-12` → fulltext 0.7, semantic 0.3.
  - Short proper-noun queries → fulltext 0.6, semantic 0.4.
  - Questions or long queries → semantic 0.6, fulltext 0.4.
- **`search_messages_hybrid(query, count, semantic_weight, full_text_weight)`** – calls the `hybrid_search` RPC, maps the results to `MessageDict`, fetches reply threads for each hit. On RPC failure falls back to `search_messages_semantic_only`.
- **`search_messages_semantic_only(query, count)`** – pure vector fallback using the old `match_messages` RPC.

The main `search_messages()` was rewritten to:
1. Call `search_messages_hybrid()` (or semantic-only if disabled).
2. Filter results by `semantic_similarity >= MIN_RESULT_SCORE` (0.1).

**Key detail:** The `similarity` field is set from `semantic_similarity` (0–1 cosine score), *not* `combined_score` (tiny RRF value ~0.01). This preserves meaningful filtering while ranking remains driven by RRF fusion from the SQL `ORDER BY`.

### `src/models/message.py`

Added optional fields to `MessageDict`: `semantic_similarity`, `full_text_rank`, `combined_score`.

### LLM answer prompt (`generate_answer`)

The system prompt was improved so the bot answers naturally without saying "based on the provided context" or similar meta-phrases. Key changes:
- "Context" → "Information".
- Explicit instructions to never reference "контекст", "предоставленная информация", etc.
- If information is insufficient, say "not sure" and suggest the links might help (instead of refusing).

---

## 3. Bugs fixed during rollout

### 3a. Type mismatch in `hybrid_search` (HTTP 400)

**Symptom:** Every `hybrid_search` call returned `400 Bad Request` with `Returned type real does not match expected type double precision in column 8`.

**Root cause:** `RETURNS TABLE` declared `combined_score float` (PostgreSQL `double precision`), but the arithmetic expression produced `real` (float4) internally.

**Fix:** Added explicit `::double precision` casts:

```sql
COALESCE(ss.similarity, 0.0)::double precision as semantic_similarity,
COALESCE(fts.rank_score, 0.0)::double precision as full_text_rank,
(COALESCE(semantic_weight / (rrf_k + ss.rank), 0.0) +
 COALESCE(full_text_weight / (rrf_k + fts.rank), 0.0))::double precision as combined_score
```

Migration: `supabase/migrations/20260214160000_fix_hybrid_search_types.sql`.

### 3b. Full-text search returning all zeros

**Symptom:** After the type fix, `hybrid_search` returned 200 OK but `full_text_rank` was `0.000` for every result.

**Root cause (1 – filtering):** The `similarity` field used in the result filter was mapped from `combined_score` (~0.01 max with RRF) instead of `semantic_similarity` (0–1). Since `MIN_RESULT_SCORE = 0.1`, every result was filtered out.

**Fix:** Changed `"similarity": r.get("combined_score", 0)` to `"similarity": r.get("semantic_similarity", 0)` in `search_messages_hybrid`.

**Root cause (2 – stemming):** `to_tsvector('simple', ...)` does no stemming and keeps stop words. Russian queries like "Какие документы нужны для стипендии" became a 5-word AND condition where ALL words (including "для", "какие") had to appear verbatim. Almost no message matched.

**Fix:** Switched from `'simple'` to `'russian'` text search configuration in all four locations:
1. Column population `UPDATE`.
2. Trigger function.
3. `ts_rank_cd(...)` in the search CTE.
4. `websearch_to_tsquery(...)` in the search CTE.

Re-indexed all 8720 existing rows. After the fix, "стипендии" stems to "стипенд", "документы" to "документ", and stop words like "для", "и", "на" are removed.

Migrations:
- `supabase/migrations/20260214170000_russian_text_search.sql` – updated trigger + function.
- `supabase/migrations/20260214190000_reindex_text_search_russian.sql` – re-populated `text_search` column for all rows.

### 3c. Full-text query too strict (AND of all words)

**Symptom:** Even with Russian stemming, fulltext contribution remained low. A query like "Какие документы нужны для стипендии?" produced `websearch_to_tsquery('russian', ...)` with all 6 words ANDed together, requiring every word to appear in a single message.

**Root cause:** The raw user question was passed directly as `query_text` to `hybrid_search`. After PostgreSQL stemming, stop words like "для" are removed, but question words and function words still inflate the AND condition, making matches unlikely.

**Fix:** Added `extract_fulltext_terms(query)` in `message_search.py` that strips Russian and English stop/question words before sending to the RPC. Two static word sets are used:

- `_RU_STOP_WORDS` – ~80 Russian question words, pronouns, prepositions, conjunctions (как, что, где, для, нужно, мне, …).
- `_EN_STOP_WORDS` – ~30 English equivalents (how, what, where, the, …).

The function also removes single-character tokens and punctuation (except hyphens for codes like `A-12`). Falls back to the original query if all words are stripped.

**Before/after examples:**

| Raw query | Extracted terms |
|---|---|
| Какие документы нужны для стипендии? | документы стипендии |
| Как проверить статус стипендии? | проверить статус стипендии |
| Что делать если пропустил запись в квестуру? | пропустил запись квестуру |
| Как получить codice fiscale в Италии? | получить codice fiscale Италии |

**Impact (evaluation run 4 vs run 3):**

Overall metrics stayed within noise (avg top similarity 0.7649 → 0.7639, keyword hit rate 32.4% → 32.2%), but category-level improvements appeared:
- vnzh_insurance: similarity +0.062 (0.635 → 0.697)
- jobs: keyword hit +20% (0% → 20%)
- deadlines: keyword hit +7.1%
- enrollment: keyword hit +4.4%
- documents: keyword hit +3.2%

Fulltext now produces non-zero scores for queries where it previously matched nothing.

---

## 4. Files added/changed

| File | Change |
|------|--------|
| `src/config/settings.py` | Added 5 hybrid search config constants |
| `src/models/message.py` | Added `semantic_similarity`, `full_text_rank`, `combined_score` fields |
| `src/services/message_search.py` | Replaced query-expansion search with hybrid search, added dynamic weights, semantic-only fallback, improved LLM prompt, added `extract_fulltext_terms` for query preprocessing |
| `sql/002_hybrid_search.sql` | New: `text_search` column, GIN index, trigger, `hybrid_search` RPC (Russian config) |
| `supabase/migrations/20260214120000_add_hybrid_search.sql` | Initial hybrid search migration |
| `supabase/migrations/20260214160000_fix_hybrid_search_types.sql` | Fix `double precision` type mismatch |
| `supabase/migrations/20260214170000_russian_text_search.sql` | Switch to `'russian'` text search config + updated function |
| `supabase/migrations/20260214190000_reindex_text_search_russian.sql` | Re-index all rows with Russian stemming |
