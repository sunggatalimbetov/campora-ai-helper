from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.services import university_service

ONBOARD_GROUP_CALLBACK_PREFIX = "onboard:group:"
ONBOARD_LANGUAGE_CALLBACK_PREFIX = "onboard:language:"


def get_available_onboarding_groups() -> list[tuple[str, str]]:
    return university_service.get_all_universities()


def resolve_group_selection_state(selected_group: str | None, available_groups: list[tuple[str, str]]) -> tuple[str | None, bool]:
    available_group_ids = {group_id for group_id, _ in available_groups}
    if selected_group in available_group_ids:
        return selected_group, False
    if len(available_groups) == 1:
        return available_groups[0][0], False
    if len(available_groups) > 1:
        return None, True
    return None, False


def create_group_keyboard(groups: list[tuple[str, str]] | None = None) -> InlineKeyboardMarkup:
    available_groups = groups or get_available_onboarding_groups()
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(group_label, callback_data=f"{ONBOARD_GROUP_CALLBACK_PREFIX}{group_id}") for group_id, group_label in available_groups]
        ]
    )
