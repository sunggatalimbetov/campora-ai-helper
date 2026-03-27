from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from src.config.settings import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS


@dataclass
class RateLimiter:
    max_requests: int = RATE_LIMIT_MAX_REQUESTS
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS
    _requests: dict = field(default_factory=lambda: defaultdict(list))

    def is_allowed(self, user_id: int, chat_id: int) -> bool:
        """Check if user is within rate limit for this chat."""
        key = (user_id, chat_id)
        now = time.time()

        self._requests[key] = [t for t in self._requests[key] if now - t < self.window_seconds]

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True


rate_limiter = RateLimiter()
