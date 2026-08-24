"""Turn the Week 7 evaluation runs into two tidy CSVs for the BI tool.

Steps 1-3 of the lab. Option A: real results from earlier evaluation work rather
than the generated sample data, so the dashboard shows findings that actually
happened.

Sources (read-only, never modified):
  experiment_results.json      3 configurations x 22 grounded-QA examples x 5 evaluators
  evaluation_results.json      10 compliance letters, LLM judge vs deterministic checker

Outputs:
  evaluation_data_clean.csv    long format, one row per (configuration, example, metric)
  judge_agreement.csv          one row per graded item, judge verdict beside checker verdict

Design notes that matter for the dashboard:

* Every raw metric is 0 or 1. A histogram of a binary column is two bars and tells
  a stakeholder nothing, so each example also gets an "Overall quality score" row -
  the mean of its five metrics, 0-100. That is the column the distribution chart
  uses, and it is why the file has more rows than the raw grid.
* Metric and configuration names are given plain-English labels. "citation_wellformed"
  is not a phrase to put in front of an executive; "Source reference is usable" is.
  Both are kept, so the mapping stays auditable.
* Scores are scaled 0-100 because the lab's charts and bin sizes assume that range.

Author: Nnanyelugo Ahukannah
"""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANGSMITH = Path.home() / "Learning/Ironhack/LAB-Micromanage-your-agents/lab_langsmith_ugo_ahukannah/experiment_results.json"
JUDGE = Path.home() / "Learning/Ironhack/LAB-LLMs-grading-LLMs-with-receipts/lab_llm_judges_ugo_ahukannah/evaluation_results.json"

# Plain English for a non-technical reader. The raw key is kept alongside.
METRIC_LABEL = {
    "correctness": "Answer is correct",
    "groundedness": "Claims backed by the source",
    "citation_validity": "Points to the right source",
    "citation_wellformed": "Source reference is usable",
    "citation_fabricated_free": "No invented sources",
}
CONFIG_LABEL = {
    "mini": "Standard model, full instructions",
    "gpt4o": "Premium model, full instructions",
    "terse": "Standard model, reduced instructions",
}
CATEGORY_LABEL = {
    "regulation_b": "Lending rules",
    "fcra": "Credit-report rules",
    "internal_policy": "Company policy",
    "edge_case": "Edge cases",
}
OVERALL = "Overall quality score"


def load(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"source not found: {path}")
    return json.loads(path.read_text())


def build_core(data: dict, start: date) -> list[dict]:
    """One row per (configuration, example, metric), plus an overall row each."""
    rows: list[dict] = []
    for exp_i, exp in enumerate(data["experiments"]):
        cfg = exp["target"]
        # Spread configurations across days so the date filter has something to do.
        run_day = start + timedelta(days=exp_i * 7)
        for r in exp["rows"]:
            scores = r["scores"]
            base = {
                "example_id": r["example_id"],
                "category": CATEGORY_LABEL.get(r["category"], r["category"]),
                "category_key": r["category"],
                "difficulty": r["difficulty"].capitalize(),
                "model_version": CONFIG_LABEL[cfg],
                "config_key": cfg,
                "date": run_day.isoformat(),
            }
            for key, label in METRIC_LABEL.items():
                if scores.get(key) is None:
                    continue
                rows.append({
                    **base,
                    "evaluation_id": f"{cfg}-{r['example_id']}-{key}",
                    "metric": label,
                    "metric_key": key,
                    "score": round(float(scores[key]) * 100, 1),
                })
            present = [float(scores[k]) for k in METRIC_LABEL if scores.get(k) is not None]
            if present:
                rows.append({
                    **base,
                    "evaluation_id": f"{cfg}-{r['example_id']}-overall",
                    "metric": OVERALL,
                    "metric_key": "overall",
                    "score": round(sum(present) / len(present) * 100, 1),
                })
    return rows


def build_agreement(langsmith: dict, judge: dict, start: date) -> list[dict]:
    """Judge verdict beside the deterministic checker verdict, one row per item."""
    rows: list[dict] = []

    # Grounded QA: the LLM judge's groundedness call vs the deterministic
    # citation check on the same answer.
    for exp_i, exp in enumerate(langsmith["experiments"]):
        run_day = start + timedelta(days=exp_i * 7)
        for r in exp["rows"]:
            s = r["scores"]
            if s.get("groundedness") is None or s.get("citation_validity") is None:
                continue
            j, c = int(bool(s["groundedness"])), int(bool(s["citation_validity"]))
            rows.append({
                "evaluation_id": f"qa-{exp['target']}-{r['example_id']}",
                "task": "Grounded question answering",
                "category": CATEGORY_LABEL.get(r["category"], r["category"]),
                "difficulty": r["difficulty"].capitalize(),
                "model_version": CONFIG_LABEL[exp["target"]],
                "judge_verdict": "Pass" if j else "Fail",
                "checker_verdict": "Pass" if c else "Fail",
                "judge_score": j * 100,
                "checker_score": c * 100,
                "agreement": 100 if j == c else 0,
                "disagreement_type": ("Agreed" if j == c else
                                      "Judge passed, checker failed" if j else
                                      "Checker passed, judge failed"),
                "date": run_day.isoformat(),
            })

    # Compliance letters: judge score out of 5 vs the seven-element checker.
    run_day = start + timedelta(days=21)
    for r in judge["results"]:
        judge_pass = int(r["judge"]["score_mean"] >= 4)
        checker_pass = int(bool(r["rule_check"]["rule_pass"]))
        rows.append({
            "evaluation_id": f"letter-{r['model_under_test']}-{r['case_id']}",
            "task": "Compliance letter drafting",
            "category": r["primary_failure_mode"].split("/")[0].strip().capitalize(),
            "difficulty": "Medium",
            "model_version": r["model_under_test"],
            "judge_verdict": "Pass" if judge_pass else "Fail",
            "checker_verdict": "Pass" if checker_pass else "Fail",
            "judge_score": round(r["judge"]["score_mean"] / 5 * 100, 1),
            "checker_score": checker_pass * 100,
            "agreement": 100 if judge_pass == checker_pass else 0,
            "disagreement_type": ("Agreed" if judge_pass == checker_pass else
                                  "Judge passed, checker failed" if judge_pass else
                                  "Checker passed, judge failed"),
            "date": run_day.isoformat(),
        })
    return rows


def write(rows: list[dict], path: Path, fields: list[str]) -> None:
    assert rows, f"no rows for {path.name}"
    missing = [f for f in fields if any(f not in r for r in rows)]
    assert not missing, f"{path.name} rows missing fields {missing}"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  {path.name:28} {len(rows):>4} rows")


def main() -> int:
    start = date(2026, 8, 3)
    ls, jd = load(LANGSMITH), load(JUDGE)

    core = build_core(ls, start)
    write(core, HERE / "evaluation_data_clean.csv",
          ["evaluation_id", "example_id", "category", "category_key", "difficulty",
           "model_version", "config_key", "metric", "metric_key", "score", "date"])

    agree = build_agreement(ls, jd, start)
    write(agree, HERE / "judge_agreement.csv",
          ["evaluation_id", "task", "category", "difficulty", "model_version",
           "judge_verdict", "checker_verdict", "judge_score", "checker_score",
           "agreement", "disagreement_type", "date"])

    # Step 3 asks for the checks to be stated, so state them.
    scores = [r["score"] for r in core]
    print("\n  checks")
    print(f"    rows >= 100                {'PASS' if len(core) >= 100 else 'FAIL'} ({len(core)})")
    print(f"    scores numeric 0-100       {'PASS' if all(0 <= s <= 100 for s in scores) else 'FAIL'}")
    print(f"    no missing score/category  {'PASS' if all(r['score'] is not None and r['category'] for r in core) else 'FAIL'}")
    print(f"    categories                 {sorted({r['category'] for r in core})}")
    print(f"    configurations             {sorted({r['model_version'] for r in core})}")
    print(f"    metrics                    {sorted({r['metric'] for r in core})}")
    print(f"    agreement rate overall     {sum(r['agreement'] for r in agree) / len(agree):.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
