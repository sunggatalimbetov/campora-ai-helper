from telegram import Update
from telegram.constants import ChatAction

from src.handlers.feedback import create_feedback_keyboard
from src.services.conversation import load_conversation_history
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.language import get_string
from src.services.message_search import generate_answer, search_messages
from src.services.message_search.rewrite_query import rewrite_query


async def run_search_flow(
    update: Update,
    *,
    query: str,
    ui_language: str,
    command_used: str,
    search_chat_id: int | None = None,
    use_typing_indicator: bool = False,
) -> None:
    """Run the shared search-answer-log-reply flow for DM, /ask, and @mention entry points."""
    user_id = update.effective_user.id
    session_chat_id = update.effective_chat.id

    with ResponseTimer() as timer:
        try:
            if use_typing_indicator:
                await update.effective_chat.send_action(ChatAction.TYPING)
            else:
                await update.message.reply_text(get_string(ui_language, "searching"))

            history, session_id = load_conversation_history(user_id, session_chat_id)
            search_query = rewrite_query(query, history)

            results, query_embedding = search_messages(search_query, chat_id=search_chat_id)
            if not results:
                no_results_message = get_string(ui_language, "no_results")
                await update.message.reply_text(no_results_message)

                await InteractionLogger.log_interaction(
                    update=update,
                    input_message=query,
                    output_message=no_results_message,
                    command_used=command_used,
                    search_results_count=0,
                    response_time_ms=timer.response_time_ms,
                    status="no_results",
                    search_query_embedding=query_embedding,
                    user_language=ui_language,
                    session_id=session_id,
                )
                return

            answer, tokens_used = generate_answer(query, results, conversation_history=history, answer_language=ui_language)

            referenced_message_ids = [msg.get("id") for msg in results if msg.get("id")]
            similarity_scores = [msg.get("similarity") for msg in results if msg.get("similarity")]

            interaction_id = await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=answer,
                command_used=command_used,
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

            if interaction_id:
                keyboard = create_feedback_keyboard(interaction_id)
                await update.message.reply_text(answer, reply_markup=keyboard)
            else:
                await update.message.reply_text(answer)

        except Exception as e:
            print(f"Error handling {command_used}: {e}")
            error_response = get_string(ui_language, "error")
            await update.message.reply_text(error_response)

            await InteractionLogger.log_interaction(
                update=update,
                input_message=query,
                output_message=error_response,
                command_used=command_used,
                response_time_ms=timer.response_time_ms,
                status="error",
                error_message=str(e),
                user_language=ui_language,
            )
