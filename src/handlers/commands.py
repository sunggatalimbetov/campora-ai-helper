from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.search_flow import run_search_flow
from src.services.conversation import mark_new_session
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import get_string, resolve_ui_language
from src.services.optout import opt_in_user, opt_out_user
from src.services.user_preferences import get_user_language


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command in group chats."""
    preferred_language = get_user_language(update.effective_user.id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=update.effective_user.language_code)

    if update.effective_chat.type == "private":
        await update.message.reply_text(get_string(ui_language, "ask_private_only"))
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text(get_string(ui_language, "ask_usage"))
        return

    chat_id = update.effective_chat.id

    await run_search_flow(
        update,
        query=query,
        ui_language=ui_language,
        command_used="/ask",
        search_chat_id=chat_id,
        use_typing_indicator=True,
    )


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset conversation history so the next question starts a fresh session."""
    mark_new_session(update.effective_user.id, update.effective_chat.id)
    preferred_language = get_user_language(update.effective_user.id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=update.effective_user.language_code)
    await update.message.reply_text(get_string(ui_language, "new_session"))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    preferred_language = get_user_language(update.effective_user.id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=update.effective_user.language_code)
    help_text = get_string(ui_language, "help")

    with ResponseTimer() as timer:
        await update.message.reply_text(help_text, parse_mode="Markdown")

        # Log help command usage
        await InteractionLogger.log_interaction(update=update, input_message="/help", output_message=help_text, command_used="/help", response_time_ms=timer.response_time_ms, status="success")
async def optout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /optout — exclude user's messages from search."""
    user_id = update.effective_user.id
    preferred_language = get_user_language(user_id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=update.effective_user.language_code)
    try:
        opt_out_user(user_id)
        await update.message.reply_text(get_string(ui_language, "optout_success"))
    except Exception as e:
        print(f"Error handling /optout: {e}")
        await update.message.reply_text(get_string(ui_language, "error"))


async def optin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /optin — re-enable message indexing."""
    user_id = update.effective_user.id
    preferred_language = get_user_language(user_id)
    ui_language = resolve_ui_language(preferred_language, telegram_language_code=update.effective_user.language_code)
    try:
        opt_in_user(user_id)
        await update.message.reply_text(get_string(ui_language, "optin_success"))
    except Exception as e:
        print(f"Error handling /optin: {e}")
        await update.message.reply_text(get_string(ui_language, "error"))
