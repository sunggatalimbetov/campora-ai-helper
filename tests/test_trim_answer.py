from __future__ import annotations

import unittest

_TRIM_MAX_CHARS = 400


def _trim_answer(answer: str) -> str:
    """Mirrors the _trim_answer logic in generate_answer.py."""
    ref_marker = "\n\nReferences"
    if ref_marker in answer:
        answer = answer[: answer.index(ref_marker)]

    if len(answer) > _TRIM_MAX_CHARS:
        answer = answer[:_TRIM_MAX_CHARS].rsplit(" ", 1)[0] + "..."

    return answer


class TrimAnswerTests(unittest.TestCase):
    def test_strips_references_section(self):
        answer = "Some answer text.\n\nReferences\n1) https://t.me/c/1/1\n2) https://t.me/c/1/2"
        self.assertEqual(_trim_answer(answer), "Some answer text.")

    def test_truncates_long_answer(self):
        long_text = "word " * 100  # 500 chars
        trimmed = _trim_answer(long_text)
        self.assertLessEqual(len(trimmed), 404)  # 400 + "..."
        self.assertTrue(trimmed.endswith("..."))

    def test_strips_references_before_truncating(self):
        short_body = "Short answer"
        refs = "\n\nReferences\n1) https://t.me/c/1/1"
        self.assertEqual(_trim_answer(short_body + refs), "Short answer")

    def test_preserves_short_answer_without_references(self):
        answer = "Quick answer about deadlines."
        self.assertEqual(_trim_answer(answer), answer)

    def test_empty_string(self):
        self.assertEqual(_trim_answer(""), "")

    def test_truncation_breaks_at_word_boundary(self):
        answer = "a " * 199 + "longword"
        trimmed = _trim_answer(answer)
        self.assertTrue(trimmed.endswith("..."))
        self.assertNotIn("longword", trimmed)

    def test_long_body_with_references_strips_then_truncates(self):
        long_body = "word " * 120  # 600 chars
        refs = "\n\nReferences\n1) https://t.me/c/1/1"
        trimmed = _trim_answer(long_body + refs)
        self.assertNotIn("References", trimmed)
        self.assertLessEqual(len(trimmed), 404)
        self.assertTrue(trimmed.endswith("..."))


if __name__ == "__main__":
    unittest.main()
