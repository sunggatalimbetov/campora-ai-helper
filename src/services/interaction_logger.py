import time
import uuid
from datetime import datetime
from typing import List, Optional

from supabase import Client, create_client
from telegram import Update

from src.config.settings import SUPABASE_SERVICE_KEY, SUPABASE_URL
from src.services.language import DEFAULT_LANGUAGE, normalize_language_code

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class InteractionLogger:
    """Service to log bot interactions to the database."""

    @staticmethod
    async def log_interaction(
        update: Update,
        input_message: str,
        output_message: str,
        command_used: Optional[str] = None,
        search_results_count: Optional[int] = None,
        referenced_message_ids: Optional[List[int]] = None,
        response_time_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        ai_model_used: str = "gpt-4o-mini",
        tokens_used: Optional[int] = None,
        search_query_embedding: Optional[List[float]] = None,
        similarity_scores: Optional[List[float]] = None,
        user_language: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Optional[int]:
        """
        Log a bot interaction to the database.
        Returns the interaction ID if successful, None otherwise.

        Args:
            update: Telegram update object
            input_message: User's input message
            output_message: Bot's response
            command_used: Command used ('/ask', 'dm', etc.)
            search_results_count: Number of search results found
            referenced_message_ids: List of message IDs used as context
            response_time_ms: Response time in milliseconds
            status: Interaction status ('success', 'error', 'no_results')
            error_message: Error message if status is 'error'
            ai_model_used: AI model used for response
            tokens_used: Number of tokens consumed
            search_query_embedding: Query embedding vector
            similarity_scores: Similarity scores from search results
            user_language: Detected user language
            session_id: Session ID for grouping related interactions
        """
        try:
            user = update.effective_user
            chat = update.effective_chat

            # Auto-generate session_id if not provided (for grouping related interactions)
            if session_id is None:
                session_id = str(uuid.uuid4())

            if user_language is None:
                user_language = DEFAULT_LANGUAGE
            else:
                user_language = normalize_language_code(user_language) or DEFAULT_LANGUAGE

            interaction_data = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "chat_id": chat.id,
                "chat_type": chat.type,
                "input_message": input_message,
                "output_message": output_message,
                "command_used": command_used,
                "search_results_count": search_results_count,
                "referenced_message_ids": referenced_message_ids,
                "response_time_ms": response_time_ms,
                "status": status,
                "error_message": error_message,
                "ai_model_used": ai_model_used,
                "tokens_used": tokens_used,
                "search_query_embedding": search_query_embedding,
                "similarity_scores": similarity_scores,
                "user_language": user_language,
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
                "user_feedback": None,
            }

            # Remove None values to avoid database issues
            interaction_data = {k: v for k, v in interaction_data.items() if v is not None}

            result = supabase.table("bot_interactions").insert(interaction_data).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None

        except Exception as e:
            print(f"Error logging interaction: {e}")
            return None

class ResponseTimer:
    """Context manager to measure response time"""

    def __init__(self):
        self.start_time = None
        self.response_time_ms = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.response_time_ms = int((time.time() - self.start_time) * 1000)
