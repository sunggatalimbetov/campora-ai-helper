from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.conversation import load_conversation_history, mark_new_session
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import get_string, resolve_query_language, resolve_ui_language
from src.services.message_search import generate_answer, search_messages
from src.services.message_search.rewrite_query import rewrite_query
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

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    query_language = resolve_query_language(query, update.effective_user.language_code)

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text(get_string(ui_language, "searching"))

            history, session_id = load_conversation_history(user_id, chat_id)
            search_query = rewrite_query(query, history)

            results, query_embedding = search_messages(search_query, chat_id=chat_id)
            if not results:
                no_results_message = get_string(ui_language, "no_results")
                await update.message.reply_text(no_results_message)

                await InteractionLogger.log_interaction(
                    update=update,
                    input_message=query,
                    output_message=no_results_message,
                    command_used="/ask",
                    search_results_count=0,
                    response_time_ms=timer.response_time_ms,
                    status="no_results",
                    search_query_embedding=query_embedding,
                    user_language=query_language,
                    session_id=session_id,
                )
                return

            answer, tokens_used = generate_answer(query, results, conversation_history=history, answer_language=query_language)

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
                user_language=query_language,
                session_id=session_id,
            )

            if interaction_id:
                keyboard = create_feedback_keyboard(interaction_id)
                await update.message.reply_text(answer, reply_markup=keyboard)
            else:
                await update.message.reply_text(answer)

        except Exception as e:
            print(f"Error handling /ask command: {e}")
            error_response = get_string(ui_language, "error")
            await update.message.reply_text(error_response)

            await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=error_response,
                command_used="/ask",
                response_time_ms=timer.response_time_ms,
                status="error",
                error_message=str(e),
                user_language=query_language,
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
