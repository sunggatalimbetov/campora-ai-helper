import os

from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI API Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

# Supabase Configuration
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")

# Hybrid search configuration
HYBRID_SEARCH_ENABLED: bool = True
DEFAULT_SEMANTIC_WEIGHT: float = 0.5
DEFAULT_FULLTEXT_WEIGHT: float = 0.5
MIN_RESULT_SCORE: float = 0.1
RRF_K: int = 60
