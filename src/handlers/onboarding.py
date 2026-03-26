from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.services.language import DEFAULT_LANGUAGE, get_language_label, get_string, normalize_language_code, resolve_ui_language
from src.services.telegram_commands import register_private_chat_commands
from src.services.user_preferences import get_user_language, get_user_preferences, save_user_language

LANGUAGE_CALLBACK_PREFIX = "language:"


def create_language_keyboard(prefix: str = LANGUAGE_CALLBACK_PREFIX) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Русский", callback_data=f"{prefix}ru"),
                InlineKeyboardButton("Қазақша", callback_data=f"{prefix}kk"),
                InlineKeyboardButton("English", callback_data=f"{prefix}en"),
            ]
        ]
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with DM onboarding and a simple group response."""
    user = update.effective_user
    preferences = get_user_preferences(user.id)
    ui_language = resolve_ui_language(
        preferences.get("language") if preferences else None,
        telegram_language_code=user.language_code,
    )

    if update.effective_chat.type != "private":
        await update.message.reply_text(get_string(ui_language, "start_group"))
        return

    if preferences and preferences.get("onboarded_at"):
        await register_private_chat_commands(context.application, update.effective_chat.id, ui_language)
        await update.message.reply_text(get_string(ui_language, "start_ready"))
        return

    await register_private_chat_commands(context.application, update.effective_chat.id, ui_language)
    await update.message.reply_text(
        f"{get_string(ui_language, 'start_welcome')}\n\n{get_string(ui_language, 'choose_language')}",
        reply_markup=create_language_keyboard(),
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow users to change their UI language preference."""
    user = update.effective_user
    preferred_language = get_user_language(user.id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=user.language_code)
    current_label = get_language_label(preferred_language or ui_language)

    await update.message.reply_text(
        get_string(ui_language, "language_command", language_label=current_label),
        reply_markup=create_language_keyboard(),
        parse_mode="Markdown",
    )


async def language_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle onboarding and /language inline button clicks."""
    query = update.callback_query
    await query.answer()

    _, selected_language = query.data.split(":", 1)
    normalized_language = normalize_language_code(selected_language) or DEFAULT_LANGUAGE
    try:
        save_user_language(query.from_user.id, normalized_language)
        await register_private_chat_commands(context.application, query.message.chat.id, normalized_language)
    except Exception as e:
        fallback_language = resolve_ui_language(None, telegram_language_code=query.from_user.language_code)
        print(f"Error saving user language: {e}")
        await query.edit_message_text(get_string(fallback_language, "error"))
        return

    await query.edit_message_text(
        get_string(normalized_language, "language_updated", language_label=get_language_label(normalized_language))
    )
