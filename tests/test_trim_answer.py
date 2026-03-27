from __future__ import annotations

import unittest

from src.utils.answer_utils import strip_references


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


if __name__ == "__main__":
    unittest.main()
