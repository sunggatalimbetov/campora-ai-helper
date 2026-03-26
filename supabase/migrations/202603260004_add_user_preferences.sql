-- Mirrors sql/007_user_preferences.sql.

CREATE TABLE IF NOT EXISTS public.user_preferences (
    user_id BIGINT PRIMARY KEY,
    selected_group TEXT,
    language TEXT NOT NULL DEFAULT 'en' CHECK (language IN ('ru', 'kk', 'en')),
    onboarded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS user_preferences_language_idx ON public.user_preferences (language);
