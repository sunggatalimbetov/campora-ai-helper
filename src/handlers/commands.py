from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.message_search import generate_answer, search_messages


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command in group chats."""
    # Only work in groups/supergroups
    if update.effective_chat.type == "private":
        await update.message.reply_text("This command works only in group chats. In private messages, just send your question directly!")
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /ask <your question>")
        return

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text("🔍 Searching, please wait...")

            results, query_embedding = search_messages(query)
            if not results:
                await update.message.reply_text("❌ No relevant messages found.")

                await InteractionLogger.log_interaction(
                    update=update,
                    input_message=query,
                    output_message="❌ No relevant messages found.",
                    command_used="/ask",
                    search_results_count=0,
                    response_time_ms=timer.response_time_ms,
                    status="no_results",
                    search_query_embedding=query_embedding,
                )
                return

            answer, tokens_used = generate_answer(query, results)
            await update.message.reply_text(answer)

            # Extract message IDs and similarity scores from results for logging
            referenced_message_ids = [msg.get("id") for msg in results if msg.get("id")]
            similarity_scores = [msg.get("similarity") for msg in results if msg.get("similarity")]

            interaction_id = await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=answer,
                command_used="/ask",
                search_results_count=len(results),
                referenced_message_ids=referenced_message_ids,
                response_time_ms=timer.response_time_ms,
                status="success",
                tokens_used=tokens_used,
                search_query_embedding=query_embedding,
                similarity_scores=similarity_scores,
            )

            if interaction_id:
                keyboard = create_feedback_keyboard(interaction_id)
                await update.message.reply_text(answer, reply_markup=keyboard)
            else:
                await update.message.reply_text(answer)

        except Exception as e:
            print(f"Error handling /ask command: {e}")
            error_response = "❌ Sorry, something went wrong. Please try again."
            await update.message.reply_text("❌ Sorry, something went wrong. Please try again.")

            await InteractionLogger.log_interaction(
                update=update, input_message=query, output_message=error_response, command_used="/ask", response_time_ms=timer.response_time_ms, status="error", error_message=str(e)
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    help_text = """🤖 *AI Assistant Bot*

*In Groups:*
• `/ask <question>` - Ask a question about the chat history
• `/help` - Show this help message

*In Private Messages:*
• Just send your question directly (no /ask needed)
• `/help` - Show this help message

*Examples:*
• In groups: `/ask What was discussed about the stipend deadline?`
• In DM: `What was discussed about the stipend deadline?`"""

    with ResponseTimer() as timer:
        await update.message.reply_text(help_text, parse_mode="Markdown")

        # Log help command usage
        await InteractionLogger.log_interaction(update=update, input_message="/help", output_message=help_text, command_used="/help", response_time_ms=timer.response_time_ms, status="success")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command (when users first message the bot)."""
    welcome_text = """👋 *Welcome to the AI Assistant Bot!*

I can help you search through chat history and answer questions.

*How to use:*
• In groups: Use `/ask <your question>`
• In private messages: Just send your question directly

*Example questions:*
• "What are the requirements for the scholarship?"
• "When is the deadline for document submission?"
• "How to apply for student housing?"

Try asking me something! 🤖"""

    with ResponseTimer() as timer:
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

        # Log start command usage
        await InteractionLogger.log_interaction(update=update, input_message="/start", output_message=welcome_text, command_used="/start", response_time_ms=timer.response_time_ms, status="success")
