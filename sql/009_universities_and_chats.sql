-- University registry and their associated Telegram chat IDs.
-- Replaces UNIME_SEARCH_CHAT_ID / NU_SEARCH_CHAT_ID env vars.
-- Run before 010_array_chat_id_filter.sql.

CREATE TABLE IF NOT EXISTS public.universities (
    id    TEXT PRIMARY KEY,  -- alias used in user_preferences.selected_group: "unime", "nu"
    label TEXT NOT NULL      -- display name shown in bot UI: "UNIME", "NU"
);

CREATE TABLE IF NOT EXISTS public.university_chats (
    university_id TEXT   NOT NULL REFERENCES public.universities(id) ON DELETE CASCADE,
    chat_id       BIGINT NOT NULL,
    PRIMARY KEY (university_id, chat_id)
);

-- Seed: fill in actual chat IDs before running.
-- INSERT INTO public.universities VALUES ('unime', 'UNIME'), ('nu', 'NU');
-- INSERT INTO public.university_chats (university_id, chat_id) VALUES
--     ('unime', <chat_id_1>),
--     ('unime', <chat_id_2>),
--     ('nu',    <chat_id_3>);
