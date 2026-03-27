import json
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
_raw_threshold = os.getenv("SIMILARITY_THRESHOLD", "0.45")
try:
    SIMILARITY_THRESHOLD: float = max(0.0, min(1.0, float(_raw_threshold)))
except ValueError:
    SIMILARITY_THRESHOLD: float = 0.45

# Conversation memory
CONVERSATION_TIMEOUT_MINUTES: int = 30
CONVERSATION_MAX_TURNS: int = 5

# Rate limiting
RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))

# Search source overrides: map a group's chat_id to a different source chat_id.
# Format: JSON object with string keys and values, e.g.
#   SEARCH_SOURCE_OVERRIDES={"<group_chat_id>": "<source_chat_id>"}
# When a /ask comes from <group_chat_id>, the search runs against <source_chat_id> instead.
_raw_overrides = os.getenv("SEARCH_SOURCE_OVERRIDES", "{}")
try:
    _parsed = {int(k): int(v) for k, v in json.loads(_raw_overrides).items()}
    # Keys are group IDs where /ask is sent. Convert positive Telethon-style IDs
    # to negative Bot API format (-100 prefix) so lookup matches update.effective_chat.id.
    SEARCH_SOURCE_OVERRIDES: dict[int, int] = {(-int(f"100{k}") if k > 0 else k): v for k, v in _parsed.items()}
except (ValueError, TypeError) as e:
    print(f"⚠️ Failed to parse SEARCH_SOURCE_OVERRIDES: {e!r}, raw={_raw_overrides!r}")
    SEARCH_SOURCE_OVERRIDES: dict[int, int] = {}
print(f"🔧 SEARCH_SOURCE_OVERRIDES = {SEARCH_SOURCE_OVERRIDES}")
