from __future__ import annotations

import time
import unittest
from unittest.mock import patch

from src.services.rate_limiter import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_allows_requests_within_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertTrue(limiter.is_allowed(1, 1))

    def test_blocks_after_limit_exceeded(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertFalse(limiter.is_allowed(1, 1))

    def test_different_users_have_separate_limits(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertTrue(limiter.is_allowed(2, 1))
        self.assertFalse(limiter.is_allowed(1, 1))

    def test_different_chats_have_separate_limits(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertTrue(limiter.is_allowed(1, 2))
        self.assertFalse(limiter.is_allowed(1, 1))

    def test_window_expiry_resets_limit(self):
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertFalse(limiter.is_allowed(1, 1))
        time.sleep(1.1)
        self.assertTrue(limiter.is_allowed(1, 1))

    def test_blocked_request_does_not_count(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        self.assertTrue(limiter.is_allowed(1, 1))
        self.assertFalse(limiter.is_allowed(1, 1))
        self.assertFalse(limiter.is_allowed(1, 1))
        # Still only 1 recorded request — blocked ones don't add entries
        self.assertEqual(len(limiter._requests[(1, 1)]), 1)


if __name__ == "__main__":
    unittest.main()
