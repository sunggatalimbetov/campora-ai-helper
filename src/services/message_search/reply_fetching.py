from typing import Dict, List, Tuple

from src.models.message import MessageDict
from src.services.message_search._clients import supabase


def fetch_replies_by_parent(messages: List[MessageDict]) -> Dict[Tuple[int, int], List[MessageDict]]:
    """
    Fetch replies for a set of parent messages in one batch query.

    Replies are grouped by (reply_to_message_id, chat_id) so parent message IDs
    that overlap across chats do not get mixed together.
    """
    if not messages:
        return {}

    parent_keys = {(msg["id"], msg["chat_id"]) for msg in messages}
    parent_ids = sorted({msg["id"] for msg in messages})
    chat_ids = sorted({msg["chat_id"] for msg in messages})

    try:
        response = (
            supabase.table("messages")
            .select("*")
            .in_("reply_to_message_id", parent_ids)
            .in_("chat_id", chat_ids)
            .execute()
        )
    except Exception as e:
        print(f"Error fetching replies batch: {e}")
        return {}

    replies_by_parent: Dict[Tuple[int, int], List[MessageDict]] = {}
    for reply in response.data or []:
        key = (reply["reply_to_message_id"], reply["chat_id"])
        if key not in parent_keys:
            continue
        replies_by_parent.setdefault(key, []).append(reply)

    return replies_by_parent


def build_reply_entries(
    messages: List[MessageDict],
    replies_by_parent: Dict[Tuple[int, int], List[MessageDict]],
) -> List[MessageDict]:
    """Build enhanced reply entries for the given parent messages."""
    reply_entries: List[MessageDict] = []
    for msg in messages:
        for reply in replies_by_parent.get((msg["id"], msg["chat_id"]), []):
            enhanced_reply: MessageDict = {
                **reply,
                "is_reply": True,
                "replying_to": msg["id"],
                "similarity": msg.get("similarity", 0),
            }
            reply_entries.append(enhanced_reply)

    return reply_entries


def attach_replies_to_messages(messages: List[MessageDict]) -> List[MessageDict]:
    """Return messages followed by any fetched replies, preserving parent order."""
    replies_by_parent = fetch_replies_by_parent(messages)

    enhanced_results: List[MessageDict] = []
    for msg in messages:
        enhanced_results.append(msg)
        enhanced_results.extend(build_reply_entries([msg], replies_by_parent))

    return enhanced_results
