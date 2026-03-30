# Feature: Rate Limiting Per Group

## Problem

Without rate limiting, a single user (or multiple users) can spam the bot in a group chat, causing:
- Flood of bot responses disrupting the group
- Unnecessary API costs (OpenAI calls for search + answer)
- Potential Telegram rate limiting on the bot itself

## Solution

Implement per-user-per-group rate limiting that caps the number of queries a user can make within a time window. When the limit is hit, silently ignore (in groups) or send a brief cooldown message (in DMs).

## Technical Design

### Rate Limiter Service

Create `src/services/rate_limiter.py`:

```python
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    max_requests: int = 10          # max queries per window
    window_seconds: int = 3600      # 1 hour window
    _requests: dict = field(default_factory=lambda: defaultdict(list))

    def is_allowed(self, user_id: int, chat_id: int) -> bool:
        """Check if user is within rate limit for this chat."""
        key = (user_id, chat_id)
        now = time.time()

        # Clean old entries
        self._requests[key] = [
            t for t in self._requests[key]
            if now - t < self.window_seconds
        ]

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True

    def remaining(self, user_id: int, chat_id: int) -> int:
        """Return remaining requests in current window."""
        key = (user_id, chat_id)
        now = time.time()
        recent = [t for t in self._requests.get(key, []) if now - t < self.window_seconds]
        return max(0, self.max_requests - len(recent))


# Global instance
rate_limiter = RateLimiter()
```

### Integration

In `ask_command` and future mention handler:

```python
from src.services.rate_limiter import rate_limiter

async def ask_command(update, context):
    if update.effective_chat.type != "private":
        if not rate_limiter.is_allowed(update.effective_user.id, update.effective_chat.id):
            return  # silently ignore in groups

    # ... rest of handler
```

In DMs (`dm_handler`), optionally show a friendly message:

```python
if not rate_limiter.is_allowed(user_id, chat_id):
    await update.message.reply_text("⏳ Too many requests. Please wait a bit before asking again.")
    return
```

### Configuration

Add to `src/config/settings.py`:

```python
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))
```

### Limitations of In-Memory Approach

- Resets on bot restart (acceptable for MVP)
- For persistence, move to a Supabase table or Redis in the future
- Memory usage is minimal: ~100 bytes per active user-chat pair

## Files to Change

- Create `src/services/rate_limiter.py` — rate limiter class
- `src/config/settings.py` — add rate limit env vars
- `src/handlers/commands.py` — add rate check in `ask_command`
- `src/handlers/messages.py` — add rate check in `dm_handler` (optional, with message)

## Implementation Checklist

- [ ] Create `src/services/rate_limiter.py`
- [ ] Add `RATE_LIMIT_MAX_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` to settings
- [ ] Integrate rate check in `ask_command` (silent skip in groups)
- [ ] Integrate rate check in `dm_handler` (with user-friendly message)
- [ ] Test: send 11 messages in a group within 1 hour → 11th is silently ignored
- [ ] Test: send 11 messages in DM → 11th gets cooldown message

## Status

Implemented
