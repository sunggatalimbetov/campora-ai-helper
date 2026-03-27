from __future__ import annotations

import unittest
from unittest.mock import patch


def _make_result(id: int, semantic_similarity: float) -> dict:
    return {
        "id": id,
        "chat_id": 1,
        "author": "test",
        "text": f"message {id}",
        "link": f"https://t.me/c/1/{id}",
        "reply_to_message_id": None,
        "created_at": None,
        "semantic_similarity": semantic_similarity,
        "full_text_rank": 0.0,
        "combined_score": semantic_similarity,
    }


def _filter(results: list[dict], threshold: float) -> list[dict]:
    """Mirrors the filter logic in search_messages_hybrid."""
    return [r for r in results if r.get("semantic_similarity", 0) >= threshold]


class SimilarityFilterTests(unittest.TestCase):
    def test_keeps_results_above_threshold(self):
        results = [_make_result(1, 0.85), _make_result(2, 0.72)]
        self.assertEqual(len(_filter(results, 0.45)), 2)

    def test_drops_results_below_threshold(self):
        results = [_make_result(1, 0.85), _make_result(2, 0.30)]
        filtered = _filter(results, 0.45)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], 1)

    def test_keeps_results_at_threshold(self):
        results = [_make_result(1, 0.45)]
        self.assertEqual(len(_filter(results, 0.45)), 1)

    def test_all_below_threshold_returns_empty(self):
        results = [_make_result(1, 0.20), _make_result(2, 0.10)]
        self.assertEqual(len(_filter(results, 0.45)), 0)

    def test_empty_results_returns_empty(self):
        self.assertEqual(len(_filter([], 0.45)), 0)

    def test_missing_similarity_field_is_dropped(self):
        result = {"id": 1, "chat_id": 1, "author": "x", "text": "y", "link": "", "reply_to_message_id": None}
        self.assertEqual(len(_filter([result], 0.45)), 0)

    def test_settings_clamps_to_bounds(self):
        with patch.dict("os.environ", {"SIMILARITY_THRESHOLD": "1.5"}):
            import importlib
            import src.config.settings as settings_mod

            importlib.reload(settings_mod)
            self.assertLessEqual(settings_mod.SIMILARITY_THRESHOLD, 1.0)

        with patch.dict("os.environ", {"SIMILARITY_THRESHOLD": "-0.5"}):
            importlib.reload(settings_mod)
            self.assertGreaterEqual(settings_mod.SIMILARITY_THRESHOLD, 0.0)

        with patch.dict("os.environ", {"SIMILARITY_THRESHOLD": "abc"}):
            importlib.reload(settings_mod)
            self.assertEqual(settings_mod.SIMILARITY_THRESHOLD, 0.45)

        # Restore default
        with patch.dict("os.environ", {}, clear=False):
            os_env = {"SIMILARITY_THRESHOLD": "0.45"}
            with patch.dict("os.environ", os_env):
                importlib.reload(settings_mod)


if __name__ == "__main__":
    unittest.main()
