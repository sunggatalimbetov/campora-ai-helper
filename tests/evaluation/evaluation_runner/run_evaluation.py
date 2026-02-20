import time
from typing import List

from src.services.message_search import generate_answer, search_messages
from tests.evaluation.test_questions import EVALUATION_QUESTIONS


def run_evaluation() -> List[dict]:
	"""Run all evaluation questions and collect results."""
	results = []

	for q in EVALUATION_QUESTIONS:
		start_time = time.time()

		# 1. Search for relevant messages
		search_results, _query_embedding = search_messages(q["question"])

		# 2. Generate answer
		answer, tokens_used = generate_answer(q["question"], search_results)

		elapsed_ms = (time.time() - start_time) * 1000

		# Similarity from original matches only (exclude reply-only entries for avg)
		similarities = [r.get("similarity", 0) for r in search_results if r.get("similarity") is not None]
		top_similarity = similarities[0] if similarities else 0.0
		avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

		# Keywords found in answer (case-insensitive)
		answer_lower = answer.lower()
		keywords_found = [kw for kw in q["expected_keywords"] if kw.lower() in answer_lower]

		result = {
			"id": q["id"],
			"question": q["question"],
			"category": q["category"],
			"num_results": len(search_results),
			"top_similarity": round(top_similarity, 4),
			"avg_similarity": round(avg_similarity, 4),
			"response_time_ms": round(elapsed_ms, 2),
			"tokens_used": tokens_used,
			"answer_preview": answer,
			"keywords_found": keywords_found,
			"keywords_missing": [k for k in q["expected_keywords"] if k not in keywords_found],
		}
		results.append(result)
		print(f"Q{q['id']}: {q['question'][:45]}... -> {result['num_results']} results, " f"top_sim={result['top_similarity']:.2f}, {result['response_time_ms']:.0f}ms")

	return results
