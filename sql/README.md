# SQL migrations

## Run with Supabase CLI (recommended)

From the project root, with [Supabase CLI](https://supabase.com/docs/guides/cli) installed:

```bash
# 1. Log in (once)
supabase login

# 2. Link this repo to your remote project (use the ref from your project URL)
supabase link --project-ref YOUR_PROJECT_REF

# 3. Push migrations to the linked project
supabase db push
```

`YOUR_PROJECT_REF` is the subdomain of your project (e.g. from `https://xgxlvvxovgrnaofggrjf.supabase.co` use `xgxlvvxovgrnaofggrjf`). You’ll be prompted for the database password (Project Settings → Database → Database password).

Migrations live in **`../supabase/migrations/`**:

- `20260213210000_create_messages_table.sql` – creates `messages` table and `match_messages` RPC
- `20260214120000_add_hybrid_search.sql` – adds `text_search` tsvector column, GIN index, trigger, and `hybrid_search` RPC for vector + full-text search
- `20260214200000_add_question_generation.sql` – creates `message_questions` table, ivfflat + message_id indexes, and `match_messages_and_questions` RPC
- `20260214210000_add_bot_interactions.sql` – creates `bot_interactions` table for storing user queries, bot responses, and like/dislike feedback
- `20260214220000_add_opted_out_users.sql` – creates `opted_out_users` for search opt-out support
- `202603260001_group_scoped_search.sql` – adds optional `filter_chat_id` parameters to retrieval RPCs so group queries stay inside their own chat
- `202603280001_add_user_preferences.sql` – creates `user_preferences` for language and onboarding state
- `202603280002_default_user_preferences_language_to_english.sql` – backfills missing user preference language values to `en`
- `202603290001_add_universities_and_chats.sql` – creates `universities` and `university_chats` for DB-backed university selection
- `202603290002_array_chat_id_filter.sql` – updates retrieval RPCs to accept `BIGINT[]` chat filters
- `202603300001_enable_rls.sql` – enables RLS on helper-owned tables; service-role access still works

---

## Run manually in the Dashboard

1. Open your [Supabase project](https://supabase.com/dashboard) → **SQL Editor**.
2. Run in order:
    - Paste the contents of `001_messages_table_and_match.sql` and click **Run**.
    - Paste the contents of `002_hybrid_search.sql` and click **Run**.
    - Paste the contents of `003_question_generation.sql` and click **Run**.
    - Paste the contents of `004_bot_interactions.sql` and click **Run**.
    - Paste the contents of `005_opted_out_users.sql` and click **Run**.
    - Paste the contents of `006_group_scoped_search.sql` and click **Run**.
    - Paste the contents of `007_user_preferences.sql` and click **Run**.
    - Paste the contents of `008_default_user_preferences_language_to_english.sql` and click **Run**.
    - Paste the contents of `009_universities_and_chats.sql` and click **Run**.
    - Paste the contents of `010_array_chat_id_filter.sql` and click **Run**.
    - Paste the contents of `011_enable_rls.sql` and click **Run**.

---

## Backfill: generate questions for existing messages

After applying the `003_question_generation.sql` migration, run the backfill script to generate hypothetical questions for all existing messages:

```bash
# From project root (uses the project virtualenv)
./env/bin/python scripts/backfill_questions.py

# Options:
#   --batch-size 10   Messages per batch (default: 10)
#   --delay 1.0       Seconds between batches (default: 1.0)
#   --limit 100       Max messages to process (default: all)
```

The script is resumable — re-running it skips messages that already have questions in `message_questions`.
