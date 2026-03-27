import unittest
import sys
import types

telegram_stub = types.ModuleType("telegram")


class MessageEntity:
    MENTION = "mention"

    def __init__(self, type: str, offset: int, length: int):
        self.type = type
        self.offset = offset
        self.length = length


telegram_stub.MessageEntity = MessageEntity
sys.modules.setdefault("telegram", telegram_stub)

from src.utils.message_filters import extract_mentioned_query


class MentionExtractionTests(unittest.TestCase):
    def test_extracts_query_when_bot_is_mentioned(self):
        text = "@campora_ai_bot when is the application deadline?"
        entities = [MessageEntity(type=MessageEntity.MENTION, offset=0, length=15)]

        query = extract_mentioned_query(text, entities, "campora_ai_bot")

        self.assertEqual(query, "when is the application deadline?")

    def test_returns_none_when_other_bot_is_mentioned(self):
        text = "@other_bot when is the application deadline?"
        entities = [MessageEntity(type=MessageEntity.MENTION, offset=0, length=10)]

        query = extract_mentioned_query(text, entities, "campora_ai_bot")

        self.assertIsNone(query)

    def test_strips_multiple_mentions_and_keeps_remaining_text(self):
        text = "@campora_ai_bot please help with the deadline @campora_ai_bot"
        entities = [
            MessageEntity(type=MessageEntity.MENTION, offset=0, length=15),
            MessageEntity(type=MessageEntity.MENTION, offset=46, length=15),
        ]

        query = extract_mentioned_query(text, entities, "campora_ai_bot")

        self.assertEqual(query, "please help with the deadline")


if __name__ == "__main__":
    unittest.main()
