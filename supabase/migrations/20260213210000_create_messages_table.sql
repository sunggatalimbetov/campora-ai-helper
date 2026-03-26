-- Reconstructed from repository history.
-- Creates the initial messages table and semantic search RPC.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.messages (
    id BIGINT PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    author BIGINT,
    text TEXT NOT NULL,
    link TEXT NOT NULL,
    embedding vector(1536),
    reply_to_message_id BIGINT
);

CREATE OR REPLACE FUNCTION public.match_messages(
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    chat_id BIGINT,
    author BIGINT,
    text TEXT,
    link TEXT,
    reply_to_message_id BIGINT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.chat_id,
        m.author,
        m.text,
        m.link,
        m.reply_to_message_id,
        (1 - (m.embedding <=> query_embedding))::float AS similarity
    FROM public.messages m
    WHERE m.embedding IS NOT NULL
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
