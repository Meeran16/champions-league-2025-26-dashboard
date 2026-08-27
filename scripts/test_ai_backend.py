from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ai.service import analyze_question
from src.data_loader import data_ready, load_all, missing_files


TEST_CASES = [
    ("Who finished first in the league phase?", "league_table"),
    ("Which team scored the most?", "top_scoring_teams"),
    ("Compare Arsenal and Bayern Munich.", "compare_teams"),
    ("Show PSG's form.", "team_form"),
    ("Who had the best away record?", "best_away_teams"),
    ("Which teams had high possession but weak results?", "high_possession_weak_results"),
    ("Which teams were efficient despite lower possession?", "efficient_low_possession"),
    ("Who is the highest-ranked forward?", "top_players"),
    ("Why does Kylian Mbappe rank above Harry Kane?", "compare_players"),
    ("Compare Thibaut Courtois and David Raya.", "compare_players"),
    ("What happened in the final?", "final_match"),
]


def main() -> None:
    if not data_ready():
        raise RuntimeError(
            "Dashboard data is missing: "
            + ", ".join(missing_files())
            + ". Run python scripts/export_dashboard_data.py first."
        )

    data = load_all()
    failures: list[str] = []

    print("AI grounding smoke test")
    print("=" * 60)

    for question, expected_intent in TEST_CASES:
        result = analyze_question(question, data)
        ok = result.intent == expected_intent
        marker = "PASS" if ok else "FAIL"
        print(f"[{marker}] {question}")
        print(f"       intent: {result.intent}")
        print(f"       answer: {result.answer}")

        if not result.answer.strip():
            failures.append(f"Empty answer: {question}")
        if result.intent != expected_intent:
            failures.append(
                f"{question!r}: expected {expected_intent}, got {result.intent}"
            )
        if result.intent != "unsupported" and not result.scope:
            failures.append(f"Missing scope: {question}")

    print("=" * 60)
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"  - {failure}")
        raise SystemExit(1)

    print(f"All {len(TEST_CASES)} grounding tests passed.")
    print("No LLM or arbitrary SQL was used.")


if __name__ == "__main__":
    main()
