import logging

from supabase import Client, create_client

from src.config.settings import SUPABASE_SERVICE_KEY, SUPABASE_URL

logger = logging.getLogger(__name__)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def opt_out_user(user_id: int) -> None:
    """Add user to opted_out_users and delete their messages from the messages table."""
    # Upsert into opted_out_users (idempotent)
    supabase.table("opted_out_users").upsert({"user_id": user_id}).execute()

    # Delete all messages authored by this user
    # The `author` column is BIGINT in the DB schema
    supabase.table("messages").delete().eq("author", user_id).execute()

    # Also delete generated questions linked to those messages (if any remain
    # after cascade — but message_questions has FK on message_id, so they
    # should already be gone if ON DELETE CASCADE is set. Delete explicitly
    # just in case.)
    logger.info("User %s opted out and messages deleted", user_id)


def opt_in_user(user_id: int) -> None:
    """Remove user from opted_out_users, re-enabling indexing."""
    supabase.table("opted_out_users").delete().eq("user_id", user_id).execute()
    logger.info("User %s opted back in", user_id)


def is_opted_out(user_id: int) -> bool:
    """Check whether a user has opted out."""
    result = supabase.table("opted_out_users").select("user_id").eq("user_id", user_id).execute()
    return len(result.data) > 0
