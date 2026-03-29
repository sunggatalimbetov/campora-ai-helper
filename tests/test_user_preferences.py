from __future__ import annotations

import unittest
from unittest.mock import patch

from src.services import user_preferences


class ResolveSelectedGroupChatIdTests(unittest.TestCase):
    def test_returns_none_without_preferences(self):
        self.assertIsNone(user_preferences.resolve_selected_group_chat_id(None))

    def test_returns_none_for_unknown_group(self):
        with patch.object(user_preferences, "ONBOARDING_GROUP_CHAT_IDS", {"nu": 123}):
            chat_id = user_preferences.resolve_selected_group_chat_id({"selected_group": "unime"})

        self.assertIsNone(chat_id)

    def test_returns_chat_id_for_known_group(self):
        with patch.object(user_preferences, "ONBOARDING_GROUP_CHAT_IDS", {"nu": 123}):
            chat_id = user_preferences.resolve_selected_group_chat_id({"selected_group": "nu"})

        self.assertEqual(chat_id, 123)


if __name__ == "__main__":
    unittest.main()
