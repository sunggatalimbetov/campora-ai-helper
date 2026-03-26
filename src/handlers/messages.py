from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.search_flow import run_search_flow
from src.services.language import get_string, resolve_ui_language
from src.services.user_preferences import get_user_language
from src.utils.message_filters import extract_mentioned_query


async def dm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct messages without requiring /ask command."""
    if update.effective_chat.type != "private":
        return

    if update.message.text and update.message.text.startswith("/"):
        return

    if not update.message.text or not update.message.text.strip():
        return

    query = update.message.text.strip()
    user_id = update.effective_user.id
    preferred_language = get_user_language(user_id)
    ui_language = resolve_ui_language(preferred_language, query, update.effective_user.language_code)

    await run_search_flow(update, query=query, ui_language=ui_language, command_used="dm")


async def group_mention_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle group messages that explicitly mention the bot username."""
    if update.effective_chat.type == "private":
        return

    if not update.message or not update.message.text or update.message.text.startswith("/"):
        return

    bot_username = getattr(context.bot, "username", None)
    if not bot_username:
        bot_username = (await context.bot.get_me()).username

    query = extract_mentioned_query(update.message.text, update.message.entities, bot_username)
    if query is None:
        return

    user_id = update.effective_user.id
    preferred_language = get_user_language(user_id)
    ui_language = resolve_ui_language(preferred_language, query, update.effective_user.language_code)

    if not query:
        await update.message.reply_text(get_string(ui_language, "mention_usage", bot_username=f"@{bot_username}"))
        return

    await run_search_flow(
        update,
        query=query,
        ui_language=ui_language,
        command_used="@mention",
        search_chat_id=update.effective_chat.id,
        use_typing_indicator=True,
    )
