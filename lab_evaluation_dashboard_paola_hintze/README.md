# Model Evaluation Score Dashboard

## Overview

This lab uses **Tableau** to communicate model evaluation results to non-technical stakeholders. The main dashboard answers three practical questions: how is the model performing overall, where does it perform best or worst, and which model or category should stakeholders inspect next? A second dashboard completes the judge agreement extension and shows how reliable the evaluation process is across categories.

## Key findings

- The full evaluation sample contains **1,800 records** across five categories, four model versions, and 90 days.
- Overall average performance is **61.9/100**.
- **Instruction following** is the strongest category at **75.1**, while **reasoning** is the clearest improvement priority at **50.9**.
- The judge agreement sample contains **900 paired evaluations**.
- Overall judge agreement is **76%** using a transparent rule: scores within 10 points count as agreement.
- Agreement is strongest for instruction following (**88%**) and weakest for reasoning (**66%**), suggesting that reasoning criteria need clearer anchors or additional calibration.

## Interactivity

The Tableau dashboard includes filters for:

- model version;
- evaluation category;
- date range.

Selecting a category in the comparison chart also filters the other performance views. The offline [`interactive_dashboard.html`](./interactive_dashboard.html) mirrors the same drill-down experience and can be opened directly in any modern browser.

## File map

| File | Purpose |
| --- | --- |
| `evaluation_score_dashboard.twbx` | Packaged Tableau workbook containing the core dashboard and judge agreement dashboard. |
| `evaluation_score_dashboard.twb` | Unpackaged Tableau workbook source for inspection and version control. |
| `judge_agreement_dashboard.twbx` | Separate packaged workbook for the optional judge agreement deliverable. |
| `screenshots/dashboard_screenshot.png` | Final core dashboard screenshot. |
| `screenshots/judge_agreement_screenshot.png` | Final judge agreement dashboard screenshot. |
| `interactive_dashboard.html` | Offline interactive companion with working filters and clickable category drill-down. |
| `data/evaluation_data_clean.csv` | Clean source table for model performance analysis. |
| `data/judge_agreement_data.csv` | Clean paired-judge source table. |
| `evaluation_dashboard_data.xlsx` | Auditable Excel companion containing both clean source tables and a guide. |
| `data_source.md` | Brief source selection and rationale. |
| `data_dictionary.md` | Field definitions and transformation rules. |
| `reflection.md` | Communication-layer reflection. |
| `dashboard_testing.md` | Test evidence and rubric coverage. |
| `rubric_self_assessment.md` | Direct evidence map for all 27 rubric criteria. |
| `generate_dashboard_assets.py` | Reproducible generator for the data, screenshots, HTML, and Tableau packages. |
| `validation_summary.json` | Machine-readable validation results. |

## How to use

1. Open `evaluation_score_dashboard.twbx` in Tableau Desktop or Tableau Public.
2. Use the model, category, and date filters in the left sidebar.
3. Select a category in the comparison chart to filter the remaining performance views.
4. Open the second Tableau dashboard to review judge agreement.

For a no-install preview, open `interactive_dashboard.html` in a browser. It is self-contained and does not load external libraries or services.

## Reproduce the assets

```bash
python -m pip install -r requirements.txt
python generate_dashboard_assets.py
```

The script uses a fixed random seed and fixed date range, so the same command produces the same records and metrics on every run.

## Data integrity note

The sample is deterministic and synthetic. It follows **Option B** in the lab instructions because the prior LLM-as-judge calibration contained only five examples, below the 100+ records recommended for meaningful distribution analysis. No simulated value is presented as a production result.
