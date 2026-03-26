from supabase import Client, create_client
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.config.settings import SUPABASE_SERVICE_KEY, SUPABASE_URL

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def create_feedback_keyboard(interaction_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with like/dislike buttons."""
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data=f"feedback:like:{interaction_id}"),
            InlineKeyboardButton("👎", callback_data=f"feedback:dislike:{interaction_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def feedback_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback button clicks."""
    query = update.callback_query
    await query.answer()

    try:
        # Parse callback data: "feedback:like/dislike:interaction_id"
        _, feedback_type, interaction_id = query.data.split(":", 2)

        if feedback_type not in {"like", "dislike"}:
            return

        result = supabase.table("bot_interactions").update({"user_feedback": feedback_type}).eq("id", int(interaction_id)).execute()

        if result.data:
            # Update the message to show feedback was recorded
            feedback_emoji = "👍" if feedback_type == "like" else "👎"
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"Thanks for feedback! {feedback_emoji}", callback_data="feedback_recorded")]]))
        else:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Error recording feedback", callback_data="feedback_error")]]))

    except Exception as e:
        print(f"Error handling feedback: {e}")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Error recording feedback", callback_data="feedback_error")]]))
