from __future__ import annotations

import unittest
from unittest.mock import patch

from src.services import onboarding_options


class OnboardingFlowTests(unittest.TestCase):
    def test_create_group_keyboard_uses_expected_callback_data(self):
        keyboard = onboarding_options.create_group_keyboard([("unime", "UNIME"), ("nu", "NU")])
        rows = keyboard.inline_keyboard

        self.assertEqual(rows[0][0].text, "UNIME")
        self.assertEqual(rows[0][0].callback_data, "onboard:group:unime")
        self.assertEqual(rows[0][1].text, "NU")
        self.assertEqual(rows[0][1].callback_data, "onboard:group:nu")

    def test_get_available_onboarding_groups_uses_configured_order(self):
        with patch.object(onboarding_options, "ONBOARDING_GROUP_CHAT_IDS", {"nu": 2, "unime": 1}):
            groups = onboarding_options.get_available_onboarding_groups()

        self.assertEqual(groups, [("unime", "UNIME"), ("nu", "NU")])


if __name__ == "__main__":
    unittest.main()
