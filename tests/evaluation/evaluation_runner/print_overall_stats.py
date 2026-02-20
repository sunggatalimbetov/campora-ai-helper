def print_overall_stats(stats: dict) -> None:
	"""Print overall stats to console in a readable format."""
	print("\n" + "=" * 60)
	print("OVERALL EVALUATION STATS")
	print("=" * 60)

	print(f"\nTotal questions: {stats['total_questions']}")

	s = stats["similarity"]
	print("\nSimilarity:")
	print(f"  Avg top similarity:  {s['avg_top_similarity']:.4f}")
	print(f"  Min top similarity:  {s['min_top_similarity']:.4f}")
	print(f"  Max top similarity:  {s['max_top_similarity']:.4f}")
	print(f"  Avg avg similarity:  {s['avg_avg_similarity']:.4f}")

	rt = stats["response_time"]
	print("\nResponse time:")
	print(f"  Average:  {rt['avg_ms']:.0f} ms")
	print(f"  Min:      {rt['min_ms']:.0f} ms")
	print(f"  Max:      {rt['max_ms']:.0f} ms")
	print(f"  Total:    {rt['total_ms'] / 1000:.1f} s")

	t = stats["tokens"]
	print("\nTokens:")
	print(f"  Avg per question:  {t['avg_per_question']:.0f}")
	print(f"  Total:             {t['total']}")

	kw = stats["keywords"]
	print("\nKeywords:")
	print(f"  Found / Expected:  {kw['total_found']} / {kw['total_expected']}")
	print(f"  Hit rate:          {kw['hit_rate']:.1%}")

	q = stats["quality"]
	print("\nQuality:")
	print(f"  Passed threshold (>= 0.3):  {q['passed_threshold']} / {stats['total_questions']} ({q['pass_rate']:.1%})")
	print(f"  Zero results:               {q['zero_results_count']}")

	print("\nCategory breakdown:")
	for cat, cs in sorted(stats["category_breakdown"].items(), key=lambda x: -x[1]["count"]):
		print(f"  {cat:25s}  n={cs['count']:3d}  avg_sim={cs['avg_top_similarity']:.3f}  kw_rate={cs['keyword_hit_rate']:.1%}  avg_time={cs['avg_response_time_ms']:.0f}ms")

	print("=" * 60)
