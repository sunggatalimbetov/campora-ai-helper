def compute_overall_stats(results: list) -> dict:
	"""Compute aggregate statistics across all evaluation results."""
	if not results:
		return {}

	total = len(results)

	# Similarity stats
	top_sims = [r["top_similarity"] for r in results]
	avg_sims = [r["avg_similarity"] for r in results]

	# Response time stats
	times = [r["response_time_ms"] for r in results]

	# Token stats
	tokens = [r["tokens_used"] for r in results]

	# Keyword stats
	total_expected = sum(len(r["keywords_found"]) + len(r["keywords_missing"]) for r in results)
	total_found = sum(len(r["keywords_found"]) for r in results)
	keyword_hit_rate = total_found / total_expected if total_expected > 0 else 0.0

	# Questions with zero results
	zero_results = sum(1 for r in results if r["num_results"] == 0)

	# Questions that passed similarity threshold (top_similarity >= 0.3)
	passed_threshold = sum(1 for r in results if r["top_similarity"] >= 0.3)

	# Category breakdown
	category_stats = {}
	for r in results:
		cat = r["category"]
		if cat not in category_stats:
			category_stats[cat] = {
				"count": 0,
				"avg_top_similarity": 0.0,
				"avg_response_time_ms": 0.0,
				"keyword_hit_rate": 0.0,
				"total_keywords": 0,
				"found_keywords": 0,
			}
		cs = category_stats[cat]
		cs["count"] += 1
		cs["avg_top_similarity"] += r["top_similarity"]
		cs["avg_response_time_ms"] += r["response_time_ms"]
		cs["total_keywords"] += len(r["keywords_found"]) + len(r["keywords_missing"])
		cs["found_keywords"] += len(r["keywords_found"])

	for cat, cs in category_stats.items():
		n = cs["count"]
		cs["avg_top_similarity"] = round(cs["avg_top_similarity"] / n, 4)
		cs["avg_response_time_ms"] = round(cs["avg_response_time_ms"] / n, 2)
		cs["keyword_hit_rate"] = round(cs["found_keywords"] / cs["total_keywords"], 4) if cs["total_keywords"] > 0 else 0.0

	return {
		"total_questions": total,
		"similarity": {
			"avg_top_similarity": round(sum(top_sims) / total, 4),
			"min_top_similarity": round(min(top_sims), 4),
			"max_top_similarity": round(max(top_sims), 4),
			"avg_avg_similarity": round(sum(avg_sims) / total, 4),
		},
		"response_time": {
			"avg_ms": round(sum(times) / total, 2),
			"min_ms": round(min(times), 2),
			"max_ms": round(max(times), 2),
			"total_ms": round(sum(times), 2),
		},
		"tokens": {
			"avg_per_question": round(sum(tokens) / total, 1),
			"total": sum(tokens),
		},
		"keywords": {
			"total_expected": total_expected,
			"total_found": total_found,
			"hit_rate": round(keyword_hit_rate, 4),
		},
		"quality": {
			"passed_threshold": passed_threshold,
			"failed_threshold": total - passed_threshold,
			"pass_rate": round(passed_threshold / total, 4),
			"zero_results_count": zero_results,
		},
		"category_breakdown": category_stats,
	}
