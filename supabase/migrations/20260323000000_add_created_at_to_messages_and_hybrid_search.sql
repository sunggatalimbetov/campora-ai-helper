-- Reconstructed from repository history.
-- Adds created_at to messages and to the semantic/hybrid search RPCs.

ALTER TABLE public.messages
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;

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
    created_at TIMESTAMPTZ,
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
        m.created_at,
        (1 - (m.embedding <=> query_embedding))::float AS similarity
    FROM public.messages m
    WHERE m.embedding IS NOT NULL
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION public.hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int DEFAULT 10,
    full_text_weight float DEFAULT 0.5,
    semantic_weight float DEFAULT 0.5,
    rrf_k int DEFAULT 60
)
RETURNS TABLE (
    id BIGINT,
    chat_id BIGINT,
    author BIGINT,
    text text,
    link text,
    reply_to_message_id BIGINT,
    created_at TIMESTAMPTZ,
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
            m.chat_id,
            m.author,
            m.text,
            m.link,
            m.reply_to_message_id,
            m.created_at,
            (1 - (m.embedding <=> query_embedding))::float as similarity,
            ROW_NUMBER() OVER (ORDER BY m.embedding <=> query_embedding) as rank
        FROM public.messages m
        WHERE m.embedding IS NOT NULL
        ORDER BY m.embedding <=> query_embedding
        LIMIT match_count * 2
    ),
    full_text_search AS (
        SELECT
            m.id,
            m.chat_id,
            m.author,
            m.text,
            m.link,
            m.reply_to_message_id,
            m.created_at,
            ts_rank_cd(m.text_search, websearch_to_tsquery('russian', query_text)) as rank_score,
            ROW_NUMBER() OVER (
                ORDER BY ts_rank_cd(m.text_search, websearch_to_tsquery('russian', query_text)) DESC
            ) as rank
        FROM public.messages m
        WHERE m.text_search IS NOT NULL
          AND trim(COALESCE(query_text, '')) <> ''
          AND m.text_search @@ websearch_to_tsquery('russian', query_text)
        ORDER BY rank_score DESC
        LIMIT match_count * 2
    ),
    combined AS (
        SELECT
            COALESCE(ss.id, fts.id) as id,
            COALESCE(ss.chat_id, fts.chat_id) as chat_id,
            COALESCE(ss.author, fts.author) as author,
            COALESCE(ss.text, fts.text) as text,
            COALESCE(ss.link, fts.link) as link,
            COALESCE(ss.reply_to_message_id, fts.reply_to_message_id) as reply_to_message_id,
            COALESCE(ss.created_at, fts.created_at) as created_at,
            COALESCE(ss.similarity, 0.0)::double precision as semantic_similarity,
            COALESCE(fts.rank_score, 0.0)::double precision as full_text_rank,
            (COALESCE(semantic_weight / (rrf_k + ss.rank), 0.0) +
             COALESCE(full_text_weight / (rrf_k + fts.rank), 0.0))::double precision as combined_score
        FROM semantic_search ss
        FULL OUTER JOIN full_text_search fts ON ss.id = fts.id
    )
    SELECT
        c.id,
        c.chat_id,
        c.author,
        c.text,
        c.link,
        c.reply_to_message_id,
        c.created_at,
        c.semantic_similarity,
        c.full_text_rank,
        c.combined_score
    FROM combined c
    ORDER BY c.combined_score DESC
    LIMIT match_count;
END;
$$;
