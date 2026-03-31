import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.handlers._search_pipeline import extract_result_metadata, run_search_pipeline
from src.handlers.feedback import create_feedback_keyboard
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import get_string, resolve_ui_language
from src.services.message_search.generate_answer import is_declined
from src.services.message_search.stream_answer import stream_answer
from src.services.rate_limiter import rate_limiter
from src.services.user_preferences import get_user_language, get_user_preferences, resolve_selected_group_chat_ids
from src.utils.answer_utils import build_references
from src.utils.streaming import StreamingResponder

logger = logging.getLogger(__name__)


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
    search_chat_ids = resolve_selected_group_chat_ids(preferences)

    if not rate_limiter.is_allowed(user_id, chat_id):
        await update.message.reply_text(get_string(ui_language, "rate_limited"))
        return

    with ResponseTimer() as timer:
        try:
            searching_msg = await update.message.reply_text(get_string(ui_language, "searching"))

            history, session_id, search_query, results, query_embedding = await run_search_pipeline(
                query, user_id, chat_id, search_chat_ids=search_chat_ids,
            )
            if not results:
                no_results_message = get_string(ui_language, "no_results")
                await searching_msg.edit_text(no_results_message)

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

            # Stream the answer, progressively editing the searching message
            responder = StreamingResponder(searching_msg)
            full_answer = ""
            tokens_used = 0

            question_results, chunks = await stream_answer(query, results, conversation_history=history, answer_language=ui_language)
            async for delta, tokens in chunks:
                if delta:
                    full_answer += delta
                    await responder.push(delta)
                if tokens is not None:
                    tokens_used = tokens

            # Build references and log interaction
            references = "" if is_declined(full_answer) else build_references(question_results, "private", language=ui_language)
            answer = full_answer + references

            referenced_message_ids, similarity_scores = extract_result_metadata(results)

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

            keyboard = create_feedback_keyboard(interaction_id) if interaction_id else None
            await responder.finalize(references=references, keyboard=keyboard)

        except Exception as e:
            logger.error("Error handling DM: %s", e)
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
