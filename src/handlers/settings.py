import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.handlers.onboarding import create_language_keyboard, LANGUAGE_CALLBACK_PREFIX
from src.services.language import get_language_label, get_string, resolve_ui_language
from src.services.onboarding_options import create_group_keyboard
from src.services.user_preferences import get_user_preferences, save_user_group
from src.services import university_service

logger = logging.getLogger(__name__)

SETTINGS_GROUP_CALLBACK_PREFIX = "settings:group:"


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current preferences and let the user change them."""
    user = update.effective_user
    preferences = get_user_preferences(user.id)
    ui_language = resolve_ui_language(
        preferences.get("language") if preferences else None,
        telegram_language_code=user.language_code,
    )

    if not preferences or not preferences.get("onboarded_at"):
        await update.message.reply_text(get_string(ui_language, "settings_not_onboarded"))
        return

    group_label = university_service.get_university_label(preferences.get("selected_group", ""))
    lang_label = get_language_label(preferences.get("language", ui_language))

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(get_string(ui_language, "settings_btn_university"), callback_data="settings:group"),
            InlineKeyboardButton(get_string(ui_language, "settings_btn_language"), callback_data="settings:lang"),
        ]
    ])
    await update.message.reply_text(
        get_string(ui_language, "settings", group_label=group_label, language_label=lang_label),
        reply_markup=keyboard,
    )


async def settings_menu_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the top-level settings button presses (group / lang)."""
    query = update.callback_query
    await query.answer()

    preferences = get_user_preferences(query.from_user.id)
    ui_language = resolve_ui_language(
        preferences.get("language") if preferences else None,
        telegram_language_code=query.from_user.language_code,
    )

    if query.data == "settings:group":
        available_groups = university_service.get_all_universities()
        keyboard = create_group_keyboard(available_groups, prefix=SETTINGS_GROUP_CALLBACK_PREFIX)
        await query.edit_message_text(
            get_string(ui_language, "choose_group"),
            reply_markup=keyboard,
        )
    elif query.data == "settings:lang":
        await query.edit_message_text(
            get_string(ui_language, "choose_language"),
            reply_markup=create_language_keyboard(prefix=LANGUAGE_CALLBACK_PREFIX),
        )


async def settings_group_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group selection from the settings flow."""
    query = update.callback_query
    await query.answer()

    selected_group = query.data.removeprefix(SETTINGS_GROUP_CALLBACK_PREFIX)
    try:
        save_user_group(query.from_user.id, selected_group)
    except Exception as e:
        fallback_language = resolve_ui_language(None, telegram_language_code=query.from_user.language_code)
        logger.error("Error saving user group in settings: %s", e)
        await query.edit_message_text(get_string(fallback_language, "error"))
        return

    preferences = get_user_preferences(query.from_user.id)
    ui_language = resolve_ui_language(
        preferences.get("language") if preferences else None,
        telegram_language_code=query.from_user.language_code,
    )
    group_label = university_service.get_university_label(selected_group)
    await query.edit_message_text(get_string(ui_language, "group_updated", group_label=group_label))
