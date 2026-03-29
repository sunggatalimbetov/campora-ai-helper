from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.config.settings import ONBOARDING_GROUP_CHAT_IDS, ONBOARDING_GROUP_LABELS

ONBOARD_GROUP_CALLBACK_PREFIX = "onboard:group:"
ONBOARD_LANGUAGE_CALLBACK_PREFIX = "onboard:language:"


def get_available_onboarding_groups() -> list[tuple[str, str]]:
    preferred_order = ("unime", "nu")
    groups: list[tuple[str, str]] = []
    for group_id in preferred_order:
        if group_id in ONBOARDING_GROUP_CHAT_IDS:
            groups.append((group_id, ONBOARDING_GROUP_LABELS.get(group_id, group_id.upper())))
    return groups


def create_group_keyboard(groups: list[tuple[str, str]] | None = None) -> InlineKeyboardMarkup:
    available_groups = groups or get_available_onboarding_groups()
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(group_label, callback_data=f"{ONBOARD_GROUP_CALLBACK_PREFIX}{group_id}") for group_id, group_label in available_groups]
        ]
    )
