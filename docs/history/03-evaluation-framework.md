# 03 – Evaluation framework

**Date:** 2026-02-14

## Summary

We built an evaluation framework to measure the bot's retrieval and answer quality. It includes 100 test questions (10 hand-crafted + 90 LLM-generated from real messages), an automated runner that collects per-question and overall statistics, and a script to generate new questions from the database.

---

## 1. Evaluation questions (`tests/evaluation/test_questions.py`)

100 questions in a single `EVALUATION_QUESTIONS` list. Each entry:

```python
{
    "id": 42,
    "question": "Как получить codice fiscale в Италии?",
    "category": "documents",
    "expected_keywords": ["agenzia", "entrate", "codice", "паспорт", "заявление"],
    "min_similarity_threshold": 0.3,
}
```

- **IDs 1–10** – hand-crafted, covering core topics (VNZh, scholarship, exams, fees, enrollment).
- **IDs 11–100** – generated from 1000 real messages by `scripts/generate_eval_questions.py`.

### Categories

Questions span: `vnzh_documents`, `scholarship`, `exams`, `fees`, `enrollment`, `documents`, `campus`, `erasmus`, `courses`, `deadlines`, `housing`, `codice_fiscale`, `transport`, and more.

---

## 2. Evaluation runner (`tests/evaluation/evaluation_runner.py`)

### Usage

```bash
python tests/evaluation/evaluation_runner.py
```

Requires `.env` with `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.

### Per-question flow

For each question the runner:

1. Calls `search_messages(question)` → retrieves messages via hybrid search.
2. Calls `generate_answer(question, results)` → LLM generates an answer.
3. Records: `num_results`, `top_similarity`, `avg_similarity`, `response_time_ms`, `tokens_used`, `keywords_found`, `keywords_missing`.

### Overall statistics (`compute_overall_stats`)

Aggregates across all questions:

| Metric group | Fields |
|---|---|
| **Similarity** | avg/min/max top similarity, avg average similarity |
| **Response time** | avg/min/max/total (ms) |
| **Tokens** | avg per question, total |
| **Keywords** | total expected, total found, hit rate |
| **Quality** | passed threshold (top_sim >= 0.3), zero-results count, pass rate |
| **Category breakdown** | per-category: count, avg similarity, keyword hit rate, avg response time |

### Output

- Console: per-question one-liner + formatted overall stats table.
- JSON: `tests/evaluation/results/evaluation_YYYYMMDD_HHMMSS.json` with `{ "overall_stats": {...}, "per_question_results": [...] }`.

---

## 3. Question generation script (`scripts/generate_eval_questions.py`)

Standalone script that automates creation of evaluation questions from real database messages.

### Usage

```bash
python scripts/generate_eval_questions.py
python scripts/generate_eval_questions.py --messages 1000 --questions 90 --batch-size 50
```

### Pipeline

1. **Fetch messages** – paginated reads from Supabase (`messages` table, newest first).
2. **Batch to LLM** – sends batches of ~50 messages to GPT-4o-mini with a prompt asking it to generate evaluation questions in Russian, with category and expected keywords. Full message text is sent (no truncation).
3. **Deduplicate** – removes identical question texts.
4. **Output** – writes both a `.py` file (matching `test_questions.py` format) and a `.json` for reference.

### Key design choices

- **No truncation** – the entire message text is passed to the LLM, per user requirement.
- **Batch rate limiting** – 1 second pause between LLM batches.
- **Per-batch cap** – max 15 questions per batch to avoid overwhelming the model.
- **Category distribution** – the script prints a category distribution summary after generation.

---

## 4. Files added

| File | Description |
|------|-------------|
| `tests/evaluation/test_questions.py` | 100 evaluation questions (10 hand-crafted + 90 generated) |
| `tests/evaluation/evaluation_runner.py` | Automated evaluation runner with per-question + overall stats |
| `tests/evaluation/results/` | Directory for JSON evaluation output files |
| `scripts/generate_eval_questions.py` | Script to generate questions from real messages via LLM |
| `tests/evaluation/generated_questions.py` | Raw generated questions in Python format |
| `tests/evaluation/generated_questions.json` | Raw generated questions in JSON format |
