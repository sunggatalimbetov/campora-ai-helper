from __future__ import annotations

import unittest

from src.utils.split_message import split_message


class SplitMessageTests(unittest.TestCase):
    def test_short_message_returns_single_chunk(self):
        text = "Short answer."
        self.assertEqual(split_message(text), [text])

    def test_exactly_at_limit_returns_single_chunk(self):
        text = "a" * 4096
        self.assertEqual(split_message(text), [text])

    def test_splits_at_paragraph_boundary(self):
        part1 = "a" * 3000
        part2 = "b" * 3000
        text = part1 + "\n\n" + part2
        chunks = split_message(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], part1)
        self.assertEqual(chunks[1], part2)

    def test_splits_at_newline_when_no_paragraph(self):
        part1 = "a" * 2000
        part2 = "b" * 2500
        text = part1 + "\n" + part2
        chunks = split_message(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], part1)

    def test_splits_at_space_when_no_newline(self):
        part1 = "word " * 800  # 4000 chars
        part2 = "more " * 100
        text = part1 + part2
        chunks = split_message(text)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 4096)

    def test_hard_cut_when_no_boundaries(self):
        text = "a" * 5000  # no spaces, newlines, or paragraphs
        chunks = split_message(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 4096)
        self.assertEqual(len(chunks[1]), 904)

    def test_empty_string(self):
        self.assertEqual(split_message(""), [""])

    def test_custom_max_length(self):
        text = "hello world foo bar"
        chunks = split_message(text, max_length=11)
        self.assertEqual(chunks[0], "hello")
        self.assertTrue(all(len(c) <= 11 for c in chunks))

    def test_all_chunks_within_limit(self):
        text = "word " * 2000  # 10000 chars
        chunks = split_message(text)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 4096)


if __name__ == "__main__":
    unittest.main()
