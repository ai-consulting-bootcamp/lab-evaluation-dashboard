# Model Evaluation Score Dashboard

This Tableau dashboard summarizes 4,489 synthetic evaluations across five task categories and four model labels from August 27 to November 24, 2026. It combines a ranking of category averages, an overall score histogram, and box plots showing the spread within each category. Date, category, and model version filters control the three views.

In the full dataset, instruction following scored highest at 72.21 out of 100, and reasoning scored lowest at 40.85. These figures describe the simulated data.

## Judge Agreement

A second Tableau dashboard summarizes 2,696 synthetic pairs of judge scores. The judges agreed within 10 points in 55.64% of pairs, and the mean absolute score difference was 10.43 points. A ranked bar chart compares agreement by category, a histogram shows the distribution of score differences, and a scatter plot compares the two judges' scores. Category and date filters support closer inspection.

| File | Purpose |
| --- | --- |
| `evaluation_score_dashboard.twbx` | Packaged interactive Tableau dashboard |
| `dashboard_screenshot.png` | Static preview of the dashboard |
| `evaluation_data_clean.csv` | Validated data used by the dashboard |
| `evaluation_data.csv` | Original generated evaluation data |
| `generate_evaluation_data.py` | Reproducible evaluation data generator |
| `judge_agreement_dashboard.twbx` | Packaged interactive dashboard for judge agreement |
| `judge_agreement_screenshot.png` | Static preview of the judge agreement dashboard |
| `judge_agreement_data.csv` | Separate synthetic dataset of paired judge scores |
| `generate_judge_agreement_data.py` | Reproducible judge agreement data generator |
| `data_source.md` | Data provenance and scoring conventions |
| `reflection.md` | Dashboard design rationale and ideas for a future version |
