# CLAUDE.md — Vectir AI Helper

## What is this?
Telegram bot that answers student questions by searching scraped university group chat history. Part of the Vectir AI system (3 repos: helper, scrapper, dashboard).

## Architecture
```
[Supabase DB] ← messages + embeddings + bot_interactions
      ↑ writes                    ↓ reads
vectir-ai-scrapper          vectir-ai-helper (this repo)
(Telethon userbot)          (python-telegram-bot)
```

## Tech Stack
- Python, python-telegram-bot
- OpenAI GPT-4o-mini (answer generation + query rewriting)
- OpenAI text-embedding-3-small (1536 dim) for search queries
- Supabase (PostgreSQL + pgvector) for hybrid search
- Search: vector cosine + Russian full-text search + Reciprocal Rank Fusion (RRF)

## Key Files
- `main.py` — bot entry point, handler registration
- `src/handlers/commands.py` — /ask, /new, /help, /start, /optout, /optin
- `src/handlers/messages.py` — DM handler (private chat messages)
- `src/handlers/feedback.py` — thumbs up/down inline keyboard
- `src/services/message_search/search_messages_hybrid.py` — hybrid search logic
- `src/services/message_search/generate_answer.py` — LLM answer synthesis with system prompt
- `src/services/message_search/rewrite_query.py` — conversation-aware query rewriting
- `src/services/conversation.py` — session/history management
- `src/services/interaction_logger.py` — logs every interaction to bot_interactions table
- `src/services/optout.py` — opt-out/opt-in user management
- `src/config/settings.py` — env vars and configuration
- `sql/` — database migrations

## What NOT to change
- Search algorithm logic (hybrid vector + FTS with RRF scoring)
- Conversation history logic
- OpenAI model choice (gpt-4o-mini) unless explicitly asked
- Project directory structure

## Coding Conventions
- Conventional commits: `feat:`, `fix:`, `refactor:`, `ci:`
- Each commit small and focused (one logical change)
- Each commit has summary line + brief description body
- New features get their own branch
- Python: follow existing code style (200 char line length, black formatting)

## Current State
- Bot works in DMs only (group mentions not yet implemented)
- Search returns results from ALL groups (not scoped by chat_id yet)
- messages table has no created_at column yet
- /optout and /optin commands exist on feat/optout-command branch

## Target Users
Kazakh and CIS university students. Groups are in Russian, Kazakh, and English. The bot must handle all three languages.

## Database Tables
- `messages` — scraped messages with embeddings (id, chat_id, author, text, link, embedding, reply_to_message_id)
- `bot_interactions` — usage logs (input, output, response_time, tokens, feedback, status)
- `opted_out_users` — users who opted out of indexing
- `chat_state` — scraper progress tracking
