from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.conversation import load_conversation_history, mark_new_session
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.message_search import generate_answer, search_messages
from src.services.message_search.rewrite_query import rewrite_query
from src.services.optout import opt_in_user, opt_out_user


async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ask command in group chats."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("This command works only in group chats. In private messages, just send your question directly!")
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /ask <your question>")
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text("🔍 Searching, please wait...")

            history, session_id = load_conversation_history(user_id, chat_id)
            search_query = rewrite_query(query, history)

            results, query_embedding = search_messages(search_query, chat_id=chat_id)
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
                    session_id=session_id,
                )
                return

            answer, tokens_used = generate_answer(query, results, conversation_history=history)

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
                session_id=session_id,
            )

            if interaction_id:
                keyboard = create_feedback_keyboard(interaction_id)
                await update.message.reply_text(answer, reply_markup=keyboard)
            else:
                await update.message.reply_text(answer)

        except Exception as e:
            print(f"Error handling /ask command: {e}")
            error_response = "❌ Sorry, something went wrong. Please try again."
            await update.message.reply_text(error_response)

            await InteractionLogger.log_interaction(
                update=update, input_message=query, output_message=error_response, command_used="/ask", response_time_ms=timer.response_time_ms, status="error", error_message=str(e)
            )


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset conversation history so the next question starts a fresh session."""
    mark_new_session(update.effective_user.id, update.effective_chat.id)
    await update.message.reply_text("🔄 Conversation reset. Your next question will start a fresh session.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    help_text = """🤖 *AI Assistant Bot*

*In Groups:*
• `/ask <question>` - Ask a question about the chat history
• `/new` - Start a fresh conversation (forget previous context)
• `/help` - Show this help message

*In Private Messages:*
• Just send your question directly (no /ask needed)
• `/new` - Start a fresh conversation
• `/help` - Show this help message

The bot remembers your recent questions so you can ask follow-ups naturally.

*Examples:*
• `/ask What was discussed about the stipend deadline?`
• Then follow up: `/ask What documents are needed?`"""

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


async def optout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /optout — exclude user's messages from search."""
    user_id = update.effective_user.id
    try:
        opt_out_user(user_id)
        await update.message.reply_text(
            "Готово. Твои сообщения удалены из базы и больше не будут индексироваться."
        )
    except Exception as e:
        print(f"Error handling /optout: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуй ещё раз.")


async def optin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /optin — re-enable message indexing."""
    user_id = update.effective_user.id
    try:
        opt_in_user(user_id)
        await update.message.reply_text(
            "Окей, теперь твои сообщения снова будут индексироваться."
        )
    except Exception as e:
        print(f"Error handling /optin: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуй ещё раз.")
