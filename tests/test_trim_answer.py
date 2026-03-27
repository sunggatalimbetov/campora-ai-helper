from __future__ import annotations

import unittest


def _strip_references(answer: str) -> str:
    """Mirrors the _strip_references logic in generate_answer.py."""
    ref_marker = "\n\nReferences"
    if ref_marker in answer:
        return answer[: answer.index(ref_marker)]
    return answer


class StripReferencesTests(unittest.TestCase):
    def test_strips_references_section(self):
        answer = "Some answer text.\n\nReferences\n1) https://t.me/c/1/1\n2) https://t.me/c/1/2"
        self.assertEqual(_strip_references(answer), "Some answer text.")

    def test_preserves_answer_without_references(self):
        answer = "Quick answer about deadlines."
        self.assertEqual(_strip_references(answer), answer)

    def test_empty_string(self):
        self.assertEqual(_strip_references(""), "")

    def test_preserves_full_answer_body(self):
        long_answer = "word " * 200  # 1000 chars, no truncation
        self.assertEqual(_strip_references(long_answer), long_answer)

    def test_strips_references_from_long_body(self):
        long_body = "word " * 200
        refs = "\n\nReferences\n1) https://t.me/c/1/1"
        self.assertEqual(_strip_references(long_body + refs), long_body)


if __name__ == "__main__":
    unittest.main()
