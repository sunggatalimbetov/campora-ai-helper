-- Reconstructed from docs/history/02-hybrid-search.md.
-- Recomputes text_search using the Russian text search config.

UPDATE public.messages
SET text_search = to_tsvector('russian', COALESCE(text, ''));
