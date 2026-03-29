from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.conversation import load_conversation_history
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import get_string, resolve_ui_language
from src.services.message_search import generate_answer, search_messages
from src.services.message_search.rewrite_query import rewrite_query
from src.services.rate_limiter import rate_limiter
from src.services.user_preferences import get_user_language, get_user_preferences, resolve_selected_group_chat_id
from src.utils.split_message import split_message


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
    preferences = get_user_preferences(user_id)
    preferred_language = preferences.get("language") if preferences else None
    ui_language = resolve_ui_language(preferred_language, query, update.effective_user.language_code)
    search_chat_id = resolve_selected_group_chat_id(preferences)

    if not rate_limiter.is_allowed(user_id, chat_id):
        await update.message.reply_text(get_string(ui_language, "rate_limited"))
        return

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text(get_string(ui_language, "searching"))

            history, session_id = load_conversation_history(user_id, chat_id)
            search_query = rewrite_query(query, history)

            results, query_embedding = search_messages(search_query, chat_id=search_chat_id)
            if not results:
                no_results_message = get_string(ui_language, "no_results")
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
                    user_language=ui_language,
                    session_id=session_id,
                )
                return

            answer, tokens_used = generate_answer(query, results, conversation_history=history, answer_language=ui_language, chat_type="private")

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
                user_language=ui_language,
                session_id=session_id,
            )

            chunks = split_message(answer)
            for i, chunk in enumerate(chunks):
                is_last = i == len(chunks) - 1
                kwargs = {"reply_markup": create_feedback_keyboard(interaction_id)} if is_last and interaction_id else {}
                try:
                    await update.message.reply_text(chunk, parse_mode="Markdown", **kwargs)
                except BadRequest as e:
                    print(f"Markdown render failed, retrying as plain text: {e}")
                    await update.message.reply_text(chunk, **kwargs)

        except Exception as e:
            print(f"Error handling DM: {e}")
            error_response = get_string(ui_language, "error")
            await update.message.reply_text(error_response)

            await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=error_response,
                command_used="dm",
                response_time_ms=timer.response_time_ms,
                status="error",
                error_message=str(e),
                user_language=ui_language,
            )
