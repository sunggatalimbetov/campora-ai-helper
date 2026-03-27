from __future__ import annotations

import unittest

_GROUP_CHAT_TYPES = {"group", "supergroup", "channel"}


def _build_references(question_results: list[dict], chat_type: str) -> str:
    """Mirrors the references logic in generate_answer.py."""
    if chat_type == "private":
        references = "\n\nReferences"
        for i, msg in enumerate(question_results, 1):
            references += f"\n{i}) {msg['link']}"
    else:
        top_refs = question_results[:2]
        references = "\n\nRef: " + " | ".join(msg["link"] for msg in top_refs) if top_refs else ""
    return references


def _make_result(id: int, link: str) -> dict:
    return {"id": id, "link": link}


class GroupAnswerReferencesTests(unittest.TestCase):
    def test_private_returns_full_numbered_references(self):
        results = [_make_result(1, "https://t.me/c/1/1"), _make_result(2, "https://t.me/c/1/2"), _make_result(3, "https://t.me/c/1/3")]
        refs = _build_references(results, "private")
        self.assertIn("References", refs)
        self.assertIn("1) https://t.me/c/1/1", refs)
        self.assertIn("3) https://t.me/c/1/3", refs)

    def test_group_returns_condensed_top_2_refs(self):
        results = [_make_result(1, "https://t.me/c/1/1"), _make_result(2, "https://t.me/c/1/2"), _make_result(3, "https://t.me/c/1/3")]
        refs = _build_references(results, "group")
        self.assertIn("Ref:", refs)
        self.assertIn("https://t.me/c/1/1", refs)
        self.assertIn("https://t.me/c/1/2", refs)
        self.assertNotIn("https://t.me/c/1/3", refs)
        self.assertNotIn("References", refs)

    def test_supergroup_uses_condensed_refs(self):
        results = [_make_result(1, "https://t.me/c/1/1")]
        refs = _build_references(results, "supergroup")
        self.assertIn("Ref:", refs)

    def test_group_empty_results_returns_empty(self):
        refs = _build_references([], "group")
        self.assertEqual(refs, "")

    def test_group_type_check_is_explicit(self):
        self.assertIn("group", _GROUP_CHAT_TYPES)
        self.assertIn("supergroup", _GROUP_CHAT_TYPES)
        self.assertIn("channel", _GROUP_CHAT_TYPES)
        self.assertNotIn("private", _GROUP_CHAT_TYPES)
        self.assertNotIn("typo", _GROUP_CHAT_TYPES)


if __name__ == "__main__":
    unittest.main()
