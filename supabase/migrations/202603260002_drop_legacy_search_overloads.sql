-- Remove legacy RPC overloads left behind before group-scoped search.
-- PostgREST cannot disambiguate overloaded RPC signatures, so keep only
-- the filter_chat_id versions introduced in 202603260001_group_scoped_search.sql.

DROP FUNCTION IF EXISTS public.hybrid_search(text, vector, integer, double precision, double precision, integer);
DROP FUNCTION IF EXISTS public.match_messages(vector, integer);
DROP FUNCTION IF EXISTS public.match_messages_and_questions(vector, integer);
