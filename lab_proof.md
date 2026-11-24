# Lab proof — Evaluation Dashboard

## Workflow and input
[Generator](generate_evaluation_data.py) uses seed 42, 90 days ending 2026-11-23, five categories and four simulated model labels. Run `python generate_evaluation_data.py`.

## Actual run evidence
[Run log](run_evidence.txt)

```text
Rows: 4489; overall mean: 55.33; dates: 2026-08-26 to 2026-11-23
                       count   mean
category
code                     914  49.62
instruction_following    898  72.21
knowledge                871  65.98
reasoning                879  40.85
tool_calling             927  48.35
```

## Output
- [Clean data](evaluation_data_clean.csv)
- [Tableau workbook draft](evaluation_score_dashboard.twb)
- [Static dashboard preview](dashboard_preview.png)
- [Source notes](data_source.md) and [reflection](reflection.md)

## Limitation and required finishing steps
Tableau Desktop is unavailable in the generation environment. The workbook XML is a draft, not a verified Tableau output. The preview is rendered in Python, not a screenshot of Tableau. Open the workbook or rebuild from the CSV if needed.

1. Connect to the cleaned CSV. Set ID/category/model to dimensions, score to measure and date to date.
2. Score Distribution: Columns score_range (discrete), Rows COUNT(evaluation_id).
3. Scores by Category: Columns category, Rows score, add evaluation_id to Detail and use Show Me > Box Plot (or use AVG(score) bar chart).
4. Category Comparison: Rows category, Columns AVG(score), sort descending, add labels.
5. Show model_version, category and date filters; Apply to Worksheets > All Using This Data Source. Add all sheets to a dashboard and use category chart as filter. Test each filter and clear selection.
6. Add score scale, synthetic-data notice and context, save packaged workbook as `evaluation_score_dashboard.twbx`, and capture `dashboard_screenshot.png` from Tableau. Commit these files and submit PR.

## Tableau execution evidence

- Successfully loaded 4,489 synthetic evaluations.
- Resolved workbook XML compatibility errors.
- Created a native Hyper data extract.
- Rendered all three charts in Tableau Public.
- Added model, category and year filter controls.

### Final deliverables

- [Tableau dashboard](evaluation_score_dashboard.twbx)
- [Actual Tableau screenshot](dashboard_screenshot.png)
- [Clean evaluation data](evaluation_data_clean.csv)

### Limitations

The date filter operates at year level.
The dataset contains synthetic evaluation results.
Cross-worksheet filter behavior requires final verification.
