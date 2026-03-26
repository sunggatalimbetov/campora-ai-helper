from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.conversation import load_conversation_history
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import detect_language, get_no_results_message
from src.services.message_search import generate_answer, search_messages
from src.services.message_search.rewrite_query import rewrite_query


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
    chat_id = update.effective_chat.id
    user_language = detect_language(query, update.effective_user.language_code)

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text("🔍 Searching, please wait...")

            history, session_id = load_conversation_history(user_id, chat_id)
            search_query = rewrite_query(query, history)

            results, query_embedding = search_messages(search_query)
            if not results:
                no_results_message = get_no_results_message(query, update.effective_user.language_code)
                await update.message.reply_text(no_results_message)

                await InteractionLogger.log_interaction(
                    update=update,
                    input_message=query,
                    output_message=no_results_message,
                    command_used="dm",
                    search_results_count=0,
                    response_time_ms=timer.response_time_ms,
                    status="no_results",
                    search_query_embedding=query_embedding,
                    user_language=user_language,
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
                command_used="dm",
                search_results_count=len(results),
                referenced_message_ids=referenced_message_ids,
                response_time_ms=timer.response_time_ms,
                status="success",
                tokens_used=tokens_used,
                search_query_embedding=query_embedding,
                similarity_scores=similarity_scores,
                user_language=user_language,
                session_id=session_id,
            )

            if interaction_id:
                keyboard = create_feedback_keyboard(interaction_id)
                await update.message.reply_text(answer, reply_markup=keyboard)
            else:
                await update.message.reply_text(answer)

        except Exception as e:
            print(f"Error handling DM: {e}")
            error_response = "❌ Sorry, something went wrong. Please try again."
            await update.message.reply_text(error_response)

            await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=error_response,
                command_used="dm",
                response_time_ms=timer.response_time_ms,
                status="error",
                error_message=str(e),
                user_language=user_language,
            )
