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
from src.handlers.commands import ask_command, help_command, start_command
from src.handlers.feedback import feedback_callback_handler
from src.handlers.messages import dm_handler

# Add logging configuration
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
client_oa: OpenAI = OpenAI(api_key=OPENAI_API_KEY)


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
            app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

            # Add handlers
            app.add_handler(CommandHandler("ask", ask_command))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(
                MessageHandler(
                    filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND,
                    dm_handler,
                )
            )
            app.add_handler(CallbackQueryHandler(feedback_callback_handler, pattern="^feedback:"))

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
