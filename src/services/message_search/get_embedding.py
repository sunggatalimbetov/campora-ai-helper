from typing import List

from src.services.message_search._clients import client_oa


def get_embedding(text: str) -> List[float]:
	"""Generate embedding for text using OpenAI."""
	response = client_oa.embeddings.create(model="text-embedding-3-small", input=text)
	return response.data[0].embedding
