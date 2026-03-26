-- Reconstructed from repository history.
-- Adds analytics and feedback logging for bot interactions.

CREATE TABLE IF NOT EXISTS public.bot_interactions (
    id                      BIGSERIAL PRIMARY KEY,
    user_id                 BIGINT NOT NULL,
    username                TEXT,
    first_name              TEXT,
    last_name               TEXT,
    chat_id                 BIGINT NOT NULL,
    chat_type               TEXT,
    input_message           TEXT NOT NULL,
    output_message          TEXT NOT NULL,
    command_used            TEXT,
    search_results_count    INTEGER,
    referenced_message_ids  BIGINT[],
    response_time_ms        INTEGER,
    status                  TEXT NOT NULL DEFAULT 'success',
    error_message           TEXT,
    ai_model_used           TEXT DEFAULT 'gpt-4o-mini',
    tokens_used             INTEGER,
    search_query_embedding  vector(1536),
    similarity_scores       DOUBLE PRECISION[],
    user_language           TEXT,
    session_id              TEXT,
    user_feedback           TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT bot_interactions_feedback_check
        CHECK (user_feedback IN ('like', 'dislike'))
);

CREATE INDEX IF NOT EXISTS bot_interactions_user_id_idx
ON public.bot_interactions (user_id);

CREATE INDEX IF NOT EXISTS bot_interactions_chat_id_idx
ON public.bot_interactions (chat_id);

CREATE INDEX IF NOT EXISTS bot_interactions_created_at_idx
ON public.bot_interactions (created_at);

CREATE INDEX IF NOT EXISTS bot_interactions_user_feedback_idx
ON public.bot_interactions (user_feedback);

CREATE INDEX IF NOT EXISTS bot_interactions_status_idx
ON public.bot_interactions (status);
