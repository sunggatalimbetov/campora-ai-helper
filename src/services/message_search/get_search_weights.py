import logging
import re
from typing import Tuple

from src.config.settings import DEFAULT_FULLTEXT_WEIGHT, DEFAULT_SEMANTIC_WEIGHT

logger = logging.getLogger(__name__)


def get_search_weights(query: str) -> Tuple[float, float]:
	"""
	Dynamically adjust search weights based on query characteristics.

	Returns:
		Tuple of (semantic_weight, full_text_weight)
	"""
	semantic_weight = DEFAULT_SEMANTIC_WEIGHT
	full_text_weight = DEFAULT_FULLTEXT_WEIGHT

	has_codes = bool(re.search(r"\b[A-Z]+[-]?\d+\b|\b\d+[-]?[A-Z]+\b", query))
	has_proper_nouns = bool(re.search(r"\b[A-Z][a-z]+\b", query))
	is_short = len(query.split()) <= 3

	if has_codes:
		full_text_weight = 0.7
		semantic_weight = 0.3
	elif is_short and has_proper_nouns:
		full_text_weight = 0.6
		semantic_weight = 0.4

	is_question = query.lower().startswith(("how", "what", "why", "when", "where", "who", "как", "что", "почему", "когда", "где", "кто"))
	is_long = len(query.split()) > 6

	if is_question or is_long:
		semantic_weight = 0.6
		full_text_weight = 0.4

	logger.debug("Query weights: semantic=%s, fulltext=%s", semantic_weight, full_text_weight)
	return semantic_weight, full_text_weight
