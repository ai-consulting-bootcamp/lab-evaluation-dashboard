"""Optional extra, Step 1 (Option A, real data): judge agreement from my W7D4 LLM Judges lab.

In that lab an LLM judge (gpt-5.4-mini) scored 10 AI-drafted loan decline letters plus 2 calibration letters
three times each, first with judge prompt v1 and then, after a failed calibration, with a clarified prompt v2.
Comparing the three runs of the same letter tells us how consistently the judge scores, i.e. how
reliable the evaluation is.

Each row = one pair of judge runs on the same letter (run 1 vs 2, 1 vs 3, 2 vs 3), so
12 letters x 3 pairs x 2 prompt versions = 72 rows.

Scores are converted from the judge's 1-5 scale to 0-100 (1 -> 0, 5 -> 100), so the dashboard uses one
scale throughout. Agreement = the two runs are within 25 points, i.e. within one step on the 1-5 scale.
"""
import itertools
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"v1 (before fix)": ROOT / "data" / "source" / "llm_judges_results_judge_v1.json",
           "v2 (after fix)": ROOT / "data" / "source" / "llm_judges_results_judge_v2.json"}
OUT = ROOT / "data" / "judge_agreement_data.csv"
AGREE_WITHIN = 25
CATEGORY = {  # test case -> plain-language category used on the dashboard
    "TC1": "Standard decline", "TC2": "Automated credit-bureau decline", "TC3": "Discriminatory note in file",
    "TC4": "Applicant in distress", "TC5": "Missing decline reason",
}

def to100(score):
    return round((score - 1) / 4 * 100, 1)

rows = []
for version, path in SOURCES.items():
    res = json.loads(path.read_text(encoding="utf-8"))
    date = res["run_info"]["timestamp_utc"][:10]
    letters = [(CATEGORY[r["case_id"][:3]], r["model"], r["judge_runs"]) for r in res["results"]]
    letters += [("Calibration letter (" + k.replace("_", " ") + ")", "hand-written reference", res["calibration"][k]["runs"])
                for k in ("known_good", "known_bad")]
    for category, model, runs in letters:
        scores = [r["score"] for r in runs]
        for (i, a), (j, b) in itertools.combinations(enumerate(scores, 1), 2):
            s1, s2 = to100(a), to100(b)
            rows.append({"judge_prompt_version": version, "category": category, "letter_written_by": model,
                         "judge_pair": f"run {i} vs run {j}", "judge_1_score": s1, "judge_2_score": s2,
                         "score_difference": round(abs(s1 - s2), 1), "agreement": int(abs(s1 - s2) <= AGREE_WITHIN),
                         "date": date})

df = pd.DataFrame(rows)
df.insert(0, "evaluation_id", range(1, len(df) + 1))
df.to_csv(OUT, index=False, encoding="utf-8")
print(f"Saved {OUT.name}: {len(df)} rows")
print("\nAgreement rate by judge prompt version:")
print(df.groupby("judge_prompt_version")["agreement"].mean().map("{:.0%}".format))
print("\nAverage score difference by version (points on 0-100):")
print(df.groupby("judge_prompt_version")["score_difference"].mean().round(1))
print("\nAgreement by category and version:")
print(df.pivot_table(index="category", columns="judge_prompt_version", values="agreement", aggfunc="mean").round(2))
