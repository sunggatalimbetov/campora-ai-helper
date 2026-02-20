from telegram import Update
from telegram.ext import ContextTypes

from src.handlers.feedback import create_feedback_keyboard
from src.services.interaction_logger import InteractionLogger, ResponseTimer
from src.services.message_search import generate_answer, search_messages


async def dm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct messages without requiring /ask command."""
    # Only respond to private messages
    if update.effective_chat.type != "private":
        return

    # Skip if it's a command (starts with /)
    if update.message.text and update.message.text.startswith("/"):
        return

    # Skip empty messages
    if not update.message.text or not update.message.text.strip():
        return

    query = update.message.text.strip()

    with ResponseTimer() as timer:
        try:
            await update.message.reply_text("🔍 Searching, please wait...")

            results, query_embedding = search_messages(query)
            if not results:
                await update.message.reply_text("❌ No relevant messages found for your question.")

                # Log the interaction with no results
                await InteractionLogger.log_interaction(
                    update=update,
                    input_message=query,
                    output_message="❌ No relevant messages found for your question.",
                    command_used="dm",
                    search_results_count=0,
                    response_time_ms=timer.response_time_ms,
                    status="no_results",
                    search_query_embedding=query_embedding,
                )
                return

            answer, tokens_used = generate_answer(query, results)
            # Extract message IDs and similarity scores from results for logging
            referenced_message_ids = [msg.get("id") for msg in results if msg.get("id")]
            similarity_scores = [msg.get("similarity") for msg in results if msg.get("similarity")]

            # Log successful interaction
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
                update=update, input_message=query, output_message=error_response, command_used="dm", response_time_ms=timer.response_time_ms, status="error", error_message=str(e)
            )
