# Evaluation Dashboard: Elif Yurdakul

**Tool:** Tableau Desktop Public Edition (free), saved locally as packaged workbooks (`.twbx`).

## Overview

**`evaluation_score_dashboard.twbx`:** a stakeholder dashboard for 4,489 model evaluations.
- KPI cards: number of evaluations, average score, share reaching the target of 70, period.
- Category comparison: average score and pass rate, sorted, with an overall-average line.
- Score distribution, colored Pass / Below target.
- Score distribution by category (box plot with a plain-language caption).
- Model × category heatmap.
- Filters for model version, category and date apply to every chart; clicking a category bar filters the dashboard.

**Headline:** only 3 in 10 evaluations reach the target. Reasoning is the weakest category (average 41, 9% pass) and instruction following the strongest (72, 59% pass). The four models score within 3 points of each other.

**`judge_agreement_dashboard.twbx` (optional extra):** shows how consistently my LLM judge from the W7D4 lab scores the same letter across three runs. Agreement rose from **78%** (judge prompt v1) to **100%** (v2), and the average gap fell from 19.4 to 1.4 points, so the fixed judge is reliable.

## Data

See [`data_source.md`](data_source.md). Main data: the lab's generated sample (Option B). Judge data: my own LLM Judges lab results (Option A).

## File map

| File / folder | Purpose |
|---|---|
| `evaluation_score_dashboard.twbx` | Main Tableau dashboard (packaged, data included) |
| `dashboard_screenshot.png` | Screenshot of the main dashboard |
| `judge_agreement_dashboard.twbx` | Optional: judge agreement dashboard |
| `judge_agreement_screenshot.png` | Optional: screenshot of the judge agreement dashboard |
| `data_source.md` | Which data I used and why (Option A vs B) |
| `reflection.md` | How I applied the communication layer, what I included and excluded |
| `BUILD_GUIDE.md` | Step-by-step Tableau build with the reasoning behind each choice |
| `data/evaluation_data.csv` | Raw generated data (Step 1) |
| `data/evaluation_data_clean.csv` | Validated data with plain-language columns (Steps 2-3); used by the main dashboard |
| `data/judge_agreement_data.csv` | Judge run-vs-run pairs, 0-100 scale; used by the optional dashboard |
| `data/source/` | Original LLM Judges lab results (judge prompt v1 and v2) |
| `scripts/generate_evaluation_data.py` | Lab's Option B generator (seed 42) |
| `scripts/clean_evaluation_data.py` | Data checks and helper columns |
| `scripts/build_judge_agreement_data.py` | Builds the judge agreement data from the lab results |

## Reproduce the data

```bash
python scripts/generate_evaluation_data.py
python scripts/clean_evaluation_data.py
python scripts/build_judge_agreement_data.py
```
Note: the generator uses "the last 90 days", so re-running it on another day shifts the dates. Scores stay identical (seed 42).
