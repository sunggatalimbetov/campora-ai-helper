from typing import List, Optional, TypedDict


class MessageDict(TypedDict):
    # Type definition for a message from the database.
    id: int
    chat_id: int
    author: str
    text: str
    link: str
    embedding: List[float]
    reply_to_message_id: Optional[int]
    created_at: Optional[str]  # ISO 8601 timestamp from Telegram message date
    similarity: Optional[float]  # Added by match_messages or hybrid_search (combined_score)
    semantic_similarity: Optional[float]  # Added by hybrid_search
    full_text_rank: Optional[float]  # Added by hybrid_search
    combined_score: Optional[float]  # Added by hybrid_search (RRF score)
    match_source: Optional[str]  # 'message' or 'question' (from match_messages_and_questions)
    is_reply: Optional[bool]  # Added when processing replies
    replying_to: Optional[int]  # Added when processing replies


class SupabaseResponse(TypedDict):
    # Type definition for Supabase response.
    data: List[MessageDict]
    count: Optional[int]


class EmbeddingResponse(TypedDict):
    # Type definition for OpenAI embedding response.
    embedding: List[float]
    index: int
    object: str


class OpenAIEmbeddingData(TypedDict):
    # Type definition for OpenAI embedding API response.
    data: List[EmbeddingResponse]
    model: str
    object: str
    usage: dict
