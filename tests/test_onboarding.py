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

    def test_resolve_group_selection_state_auto_selects_single_group(self):
        resolved_group, should_prompt = onboarding_options.resolve_group_selection_state(None, [("nu", "NU")])

        self.assertEqual(resolved_group, "nu")
        self.assertFalse(should_prompt)

    def test_resolve_group_selection_state_prompts_when_multiple_groups_exist(self):
        resolved_group, should_prompt = onboarding_options.resolve_group_selection_state(None, [("unime", "UNIME"), ("nu", "NU")])

        self.assertIsNone(resolved_group)
        self.assertTrue(should_prompt)


if __name__ == "__main__":
    unittest.main()
