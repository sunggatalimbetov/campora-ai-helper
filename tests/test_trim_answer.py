from __future__ import annotations

import unittest

from src.utils.answer_utils import strip_references, trim_answer_for_history


class StripReferencesTests(unittest.TestCase):
    def test_strips_references_section(self):
        answer = "Some answer text.\n\nReferences\n1) https://t.me/c/1/1\n2) https://t.me/c/1/2"
        self.assertEqual(strip_references(answer), "Some answer text.")

    def test_preserves_answer_without_references(self):
        answer = "Quick answer about deadlines."
        self.assertEqual(strip_references(answer), answer)

    def test_empty_string(self):
        self.assertEqual(strip_references(""), "")

    def test_preserves_full_answer_body(self):
        long_answer = "word " * 200
        self.assertEqual(strip_references(long_answer), long_answer)

    def test_strips_references_from_long_body(self):
        long_body = "word " * 200
        refs = "\n\nReferences\n1) https://t.me/c/1/1"
        self.assertEqual(strip_references(long_body + refs), long_body)


class TrimAnswerForHistoryTests(unittest.TestCase):
    def test_keeps_short_answer_unchanged(self):
        answer = "Quick answer about deadlines."
        self.assertEqual(trim_answer_for_history(answer), answer)

    def test_strips_references_before_truncation(self):
        answer = "Core answer text.\n\n📎 Sources:\n1. [preview](https://t.me/c/1/1)"
        self.assertEqual(trim_answer_for_history(answer), "Core answer text.")

    def test_truncates_long_answer_at_word_boundary(self):
        answer = "word " * 100
        trimmed = trim_answer_for_history(answer, max_chars=40)
        self.assertTrue(trimmed.endswith("..."))
        self.assertLessEqual(len(trimmed), 43)
        self.assertNotIn("\n\nReferences", trimmed)

    def test_falls_back_to_hard_cut_when_no_spaces_exist(self):
        answer = "x" * 50
        self.assertEqual(trim_answer_for_history(answer, max_chars=10), "xxxxxxxxxx...")


if __name__ == "__main__":
    unittest.main()
