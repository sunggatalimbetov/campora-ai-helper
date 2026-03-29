from __future__ import annotations

import unittest
from unittest.mock import patch

from src.services import user_preferences


class ResolveSelectedGroupChatIdsTests(unittest.TestCase):
    def test_returns_none_without_preferences(self):
        self.assertIsNone(user_preferences.resolve_selected_group_chat_ids(None))

    def test_returns_none_when_selected_group_missing(self):
        self.assertIsNone(user_preferences.resolve_selected_group_chat_ids({}))

    def test_returns_none_for_unknown_group(self):
        with patch("src.services.user_preferences.university_service.get_chat_ids_for_university", return_value=[]):
            result = user_preferences.resolve_selected_group_chat_ids({"selected_group": "unime"})
        self.assertIsNone(result)

    def test_returns_chat_ids_for_known_group(self):
        with patch("src.services.user_preferences.university_service.get_chat_ids_for_university", return_value=[123, 456]):
            result = user_preferences.resolve_selected_group_chat_ids({"selected_group": "unime"})
        self.assertEqual(result, [123, 456])


class SaveUserGroupValidationTests(unittest.TestCase):
    def test_raises_for_unknown_group(self):
        with patch("src.services.user_preferences.university_service.get_chat_ids_for_university", return_value=[]):
            with self.assertRaises(ValueError):
                user_preferences.save_user_group(1, "unime")


if __name__ == "__main__":
    unittest.main()
