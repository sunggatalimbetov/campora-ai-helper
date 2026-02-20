import json
import sys
import time
from pathlib import Path

# Ensure project root is on path (for both direct run and -m)
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
	sys.path.insert(0, str(_project_root))

from tests.evaluation.evaluation_runner import (  # noqa: E402
	compute_overall_stats,
	print_overall_stats,
	run_evaluation,
)
from tests.evaluation.test_questions import EVALUATION_QUESTIONS  # noqa: E402


def main():
	"""Run evaluation and save results to JSON."""
	print("Running evaluation with", len(EVALUATION_QUESTIONS), "questions...\n")
	results = run_evaluation()

	# Compute overall stats
	overall_stats = compute_overall_stats(results)

	# Print stats to console
	print_overall_stats(overall_stats)

	results_dir = Path(__file__).resolve().parent.parent / "results"
	results_dir.mkdir(exist_ok=True)
	timestamp = time.strftime("%Y%m%d_%H%M%S")
	out_path = results_dir / f"evaluation_{timestamp}.json"

	# Build output with both per-question results and overall stats
	output = {
		"overall_stats": overall_stats,
		"per_question_results": [{k: v for k, v in r.items()} for r in results],
	}

	with open(out_path, "w", encoding="utf-8") as f:
		json.dump(output, f, ensure_ascii=False, indent=2)

	print(f"\nResults saved to {out_path}")
	return results


if __name__ == "__main__":
	main()
