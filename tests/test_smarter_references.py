from __future__ import annotations

import unittest

from src.utils.answer_utils import build_references, strip_references


def _make_result(id: int, text: str, link: str) -> dict:
    return {"id": id, "text": text, "link": link}


class BuildReferencesTests(unittest.TestCase):
    def test_private_returns_labeled_inline_links(self):
        results = [_make_result(1, "Deadline is March 15th for enrollment", "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="en")
        self.assertIn("📎 Sources:", refs)
        self.assertIn("[Deadline is March 15th for enrollment](https://t.me/c/1/1)", refs)

    def test_group_returns_top_2_only(self):
        results = [
            _make_result(1, "First message", "https://t.me/c/1/1"),
            _make_result(2, "Second message", "https://t.me/c/1/2"),
            _make_result(3, "Third message", "https://t.me/c/1/3"),
        ]
        refs = build_references(results, "group", language="en")
        self.assertIn("https://t.me/c/1/1", refs)
        self.assertIn("https://t.me/c/1/2", refs)
        self.assertNotIn("https://t.me/c/1/3", refs)

    def test_preview_truncates_long_text(self):
        long_text = "word " * 30  # 150 chars
        results = [_make_result(1, long_text, "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="en")
        self.assertIn("...", refs)
        # The preview part (inside brackets) should be under ~83 chars (80 + "...")
        bracket_start = refs.index("[") + 1
        bracket_end = refs.index("]")
        preview = refs[bracket_start:bracket_end]
        self.assertLessEqual(len(preview), 84)

    def test_preview_strips_newlines(self):
        results = [_make_result(1, "Line one\nLine two\nLine three", "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="en")
        self.assertNotIn("\nLine", refs.split("📎")[1])

    def test_russian_header(self):
        results = [_make_result(1, "Тест", "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="ru")
        self.assertIn("📎 Источники:", refs)

    def test_kazakh_header(self):
        results = [_make_result(1, "Тест", "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="kk")
        self.assertIn("📎 Дереккөздер:", refs)

    def test_empty_results_returns_empty(self):
        self.assertEqual(build_references([], "private"), "")
        self.assertEqual(build_references([], "group"), "")

    def test_escapes_markdown_brackets(self):
        results = [_make_result(1, "Use [this] function(x)", "https://t.me/c/1/1")]
        refs = build_references(results, "private", language="en")
        # Characters must be escaped (backslash-prefixed), not deleted
        label = refs.split("📎")[1].split("](")[0]
        self.assertIn("\\[", label)
        self.assertIn("\\]", label)
        self.assertIn("\\(", label)
        self.assertIn("\\)", label)
        # Original text content must be preserved
        self.assertIn("this", label)
        self.assertIn("function", label)


class StripReferencesTests(unittest.TestCase):
    def test_strips_new_localized_header_en(self):
        answer = "Some answer.\n\n📎 Sources:\n1. [preview](https://t.me/c/1/1)"
        self.assertEqual(strip_references(answer), "Some answer.")

    def test_strips_new_localized_header_ru(self):
        answer = "Ответ.\n\n📎 Источники:\n1. [превью](https://t.me/c/1/1)"
        self.assertEqual(strip_references(answer), "Ответ.")

    def test_strips_legacy_references_header(self):
        answer = "Answer.\n\nReferences\n1) https://t.me/c/1/1"
        self.assertEqual(strip_references(answer), "Answer.")


if __name__ == "__main__":
    unittest.main()
