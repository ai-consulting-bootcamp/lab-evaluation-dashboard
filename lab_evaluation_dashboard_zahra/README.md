# Evaluation Dashboard

**Tool used:** Tableau Public (web version)

## What this dashboard shows

A dashboard called "Model Evaluation Score Dashboard" with 3 charts:
- Score Distribution, a histogram of all scores in bins of 10
- Scores by Category, average score for each of the 5 categories
- Category Comparison, the same averages sorted from highest to lowest, with a color scale

It has filters for category, model version, and date, and they control all 3 charts together. Scores go from 0 to 100. `reasoning` is the weakest category at 40.85, `instruction_following` is the strongest at 72.21.

## Data source

I used the sample data generator from `instructions.md` (Option B). See `data_source.md` for details.

## File map

- `data/generate_evaluation_data.py`: makes the raw sample data (Step 1)
- `data/clean_and_check.py`: checks and cleans the raw data, writes the report (Step 2)
- `data/evaluation_data.csv`: raw generated data
- `data/evaluation_data_clean.csv`: cleaned data, this is what was loaded into Tableau
- `data/cleaning_check.md`: result of the cleaning check
- `data_source.md`: which data option was used and why
- `evaluation_score_dashboard.twbx`: the Tableau workbook
- `dashboard_screenshot.png`: screenshot of the final dashboard
- `reflection.md`: what I learned building this
