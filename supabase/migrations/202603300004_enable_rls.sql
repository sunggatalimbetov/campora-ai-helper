-- Enable RLS on helper-owned tables.
-- Service-role clients continue to work; anon/authenticated clients need policies.
-- Safe to run multiple times.

DO $$
DECLARE
    table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'messages',
        'message_questions',
        'bot_interactions',
        'opted_out_users',
        'user_preferences',
        'universities',
        'university_chats',
        'chat_state'
    ]
    LOOP
        IF EXISTS (
            SELECT 1
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename = table_name
        ) THEN
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
        END IF;
    END LOOP;
END
$$;
