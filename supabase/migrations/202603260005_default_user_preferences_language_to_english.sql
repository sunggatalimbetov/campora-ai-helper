ALTER TABLE public.user_preferences
ALTER COLUMN language SET DEFAULT 'en';

UPDATE public.user_preferences
SET language = 'en'
WHERE language IS NULL;
