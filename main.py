import asyncio
import logging
import time

from openai import OpenAI
from supabase import Client, create_client
from telegram import Update
from telegram.error import Conflict, NetworkError, RetryAfter
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.config.settings import (
    OPENAI_API_KEY,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
    TELEGRAM_BOT_TOKEN,
)
from src.handlers.commands import ask_command, help_command, new_command, optin_command, optout_command
from src.handlers.feedback import feedback_callback_handler
from src.handlers.messages import dm_handler
from src.handlers.onboarding import language_callback_handler, language_command, start_command
from src.services.telegram_commands import register_default_bot_commands

# Add logging configuration
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
client_oa: OpenAI = OpenAI(api_key=OPENAI_API_KEY)


WELCOME_NOTICE_TEMPLATE = (
    "👋 Привет! Я Campora AI — помогаю находить ответы по истории переписки этой группы.\n\n"
    "Как использовать:\n"
    "• /ask <вопрос>\n"
    "• @{bot_username} <вопрос>\n"
    "• /help — все команды\n\n"
    "Если не хочешь, чтобы твои сообщения использовались — напиши /optout."
)

# Track chats that already received the welcome notice (per bot session).
# For persistence across restarts, you could store this in Supabase instead.
_notified_chats: set[int] = set()


async def register_bot_commands(app: Application) -> None:
    """Register Telegram slash commands so clients can show the command menu."""
    bot_username = (await app.bot.get_me()).username
    app.bot_data["bot_username"] = bot_username
    await register_default_bot_commands(app)
    logger.info("Telegram slash commands registered for @%s", bot_username)


async def track_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a one-time opt-out notice when the bot is added to a group."""
    if update.my_chat_member is None:
        return

    new_status = update.my_chat_member.new_chat_member.status
    chat = update.my_chat_member.chat

    # Bot was added or promoted in a group
    if new_status in ("member", "administrator") and chat.id not in _notified_chats:
        _notified_chats.add(chat.id)
        try:
            bot_username = context.application.bot_data.get("bot_username") or context.bot.username
            await context.bot.send_message(chat_id=chat.id, text=WELCOME_NOTICE_TEMPLATE.format(bot_username=bot_username))
        except Exception as e:
            logger.warning("Could not send welcome notice to chat %s: %s", chat.id, e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors caused by updates."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    if isinstance(context.error, Conflict):
        logger.warning("Conflict error - waiting 30 seconds before retry...")
        await asyncio.sleep(30)
    elif isinstance(context.error, NetworkError):
        logger.warning("Network error - waiting 10 seconds before retry...")
        await asyncio.sleep(10)
    elif isinstance(context.error, RetryAfter):
        retry_after = context.error.retry_after
        logger.warning(f"Rate limited - waiting {retry_after} seconds...")
        await asyncio.sleep(retry_after)


def main():
    """Start the bot with retry logic."""
    while True:
        try:
            # Create the Application
            app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(register_bot_commands).build()

            # Add handlers
            app.add_handler(CommandHandler("ask", ask_command))
            app.add_handler(CommandHandler("new", new_command))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CommandHandler("language", language_command))
            app.add_handler(CommandHandler("optout", optout_command))
            app.add_handler(CommandHandler("optin", optin_command))
            app.add_handler(
                MessageHandler(
                    filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
                    dm_handler,
                )
            )
            app.add_handler(CallbackQueryHandler(feedback_callback_handler, pattern="^feedback:"))
            app.add_handler(CallbackQueryHandler(language_callback_handler, pattern=r"^(language:|onboard:group:|onboard:language:)"))
            app.add_handler(ChatMemberHandler(track_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

            # Add error handler
            app.add_error_handler(error_handler)

            print("🤖 Starting AI Assistant Bot...")

            # Start the bot with graceful shutdown
            app.run_polling(allowed_updates=Update.ALL_TYPES)

        except Conflict as e:
            logger.error(f"Conflict error: {e}")
            print("⚠️ Conflict detected. Waiting 30 seconds before restart...")
            time.sleep(30)
            continue
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print("⚠️ Unexpected error. Waiting 10 seconds before restart...")
            time.sleep(10)
            continue


if __name__ == "__main__":
    main()
