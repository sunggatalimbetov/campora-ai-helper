# Campora AI Helper

Telegram bot that answers university student questions by searching scraped group chat history using hybrid semantic and full-text search.

## Features

- **Hybrid Search** — combines vector similarity + full-text search with Reciprocal Rank Fusion (RRF) scoring
- **Multi-language** — Russian, Kazakh, and English with localized UI
- **Conversation Context** — maintains session history for follow-up questions with automatic query rewriting
- **Group & DM Support** — auto-search in DMs, explicit `/ask` command in groups
- **User Feedback** — thumbs up/down on responses, logged for analytics
- **Privacy Controls** — `/optout` and `/optin` commands for message indexing

## Tech Stack

- **Python** with python-telegram-bot (async)
- **OpenAI** — GPT-4o-mini for answers, text-embedding-3-small for embeddings
- **Supabase** — PostgreSQL + pgvector for hybrid search
- **Streamlit** — analytics via [vectir-ai-dashboard](https://github.com/sunggatalimbetov/vectir-ai-dashboard)

## Prerequisites

- Python 3.9+
- Telegram bot token (from [@BotFather](https://t.me/BotFather))
- OpenAI API key
- Supabase project with pgvector enabled

## Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your-bot-token
OPENAI_API_KEY=your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Apply database migrations
supabase link --project-ref YOUR_PROJECT_REF
supabase db push

# Run the bot
python main.py
```

## Project Structure

```
src/
├── config/          # Environment variables and constants
├── models/          # TypedDict definitions
├── handlers/        # Bot command and message handlers
├── services/
│   ├── message_search/  # Hybrid search, embeddings, answer generation
│   ├── conversation.py  # Session and history management
│   ├── language.py      # i18n strings and language resolution
│   ├── optout.py        # User opt-in/out for indexing
│   └── ...
└── utils/           # Text preprocessing utilities
sql/                 # Database migrations
docs/features/       # Feature specifications
```

## Bot Commands

| Command     | Description                          |
|-------------|--------------------------------------|
| `/start`    | Onboarding flow with language select |
| `/ask`      | Ask a question (required in groups)  |
| `/new`      | Reset conversation session           |
| `/language` | Change UI language                   |
| `/help`     | Show help message                    |
| `/optout`   | Exclude your messages from indexing  |
| `/optin`    | Re-include your messages in indexing |

## Related Repos

- [vectir-ai-scrapper](https://github.com/sunggatalimbetov/vectir-ai-scrapper) — Telegram group message scraper
- [vectir-ai-dashboard](https://github.com/sunggatalimbetov/vectir-ai-dashboard) — Analytics dashboard
