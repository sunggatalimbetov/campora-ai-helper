from __future__ import annotations

import unittest

from src.utils.answer_utils import GROUP_CHAT_TYPES, build_references


def _make_result(id: int, link: str) -> dict:
    return {"id": id, "link": link}


class GroupAnswerReferencesTests(unittest.TestCase):
    def test_private_returns_full_numbered_references(self):
        results = [_make_result(1, "https://t.me/c/1/1"), _make_result(2, "https://t.me/c/1/2"), _make_result(3, "https://t.me/c/1/3")]
        refs = build_references(results, "private")
        self.assertIn("References", refs)
        self.assertIn("1) https://t.me/c/1/1", refs)
        self.assertIn("3) https://t.me/c/1/3", refs)

    def test_group_returns_condensed_top_2_refs(self):
        results = [_make_result(1, "https://t.me/c/1/1"), _make_result(2, "https://t.me/c/1/2"), _make_result(3, "https://t.me/c/1/3")]
        refs = build_references(results, "group")
        self.assertIn("Ref:", refs)
        self.assertIn("https://t.me/c/1/1", refs)
        self.assertIn("https://t.me/c/1/2", refs)
        self.assertNotIn("https://t.me/c/1/3", refs)
        self.assertNotIn("References", refs)

    def test_supergroup_uses_condensed_refs(self):
        results = [_make_result(1, "https://t.me/c/1/1")]
        refs = build_references(results, "supergroup")
        self.assertIn("Ref:", refs)

    def test_channel_uses_condensed_refs(self):
        results = [_make_result(1, "https://t.me/c/1/1")]
        refs = build_references(results, "channel")
        self.assertIn("Ref:", refs)

    def test_group_empty_results_returns_empty(self):
        refs = build_references([], "group")
        self.assertEqual(refs, "")

    def test_private_empty_results_returns_empty(self):
        refs = build_references([], "private")
        self.assertEqual(refs, "")

    def test_group_type_check_is_explicit(self):
        self.assertIn("group", GROUP_CHAT_TYPES)
        self.assertIn("supergroup", GROUP_CHAT_TYPES)
        self.assertIn("channel", GROUP_CHAT_TYPES)
        self.assertNotIn("private", GROUP_CHAT_TYPES)
        self.assertNotIn("typo", GROUP_CHAT_TYPES)


if __name__ == "__main__":
    unittest.main()
