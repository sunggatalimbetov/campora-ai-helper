-- Opt-out support: users can request their messages be excluded from search.
-- The scrapper (campora-ai-scrapper) should also check this table before ingesting
-- new messages: skip any message where author is in opted_out_users.

CREATE TABLE IF NOT EXISTS public.opted_out_users (
    user_id BIGINT PRIMARY KEY,
    opted_out_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS opted_out_users_user_id_idx ON public.opted_out_users (user_id);
