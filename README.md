# Evaluation Dashboard Lab


## Project Overview

This lab demonstrates how AI model evaluation results can be communicated to non-technical stakeholders through an interactive Tableau dashboard.

The dashboard presents 4,489 synthetic evaluation records across five categories and four model versions, covering 26 August to 23 November 2026.

## Interactive Dashboard

[View the published Tableau dashboard](https://public.tableau.com/app/profile/martha.olukayode/viz/AIModelEvaluationPerformanceDashboard/Dashboard1)

The dashboard contains three visualizations:

1. **Score Distribution:** Histogram showing evaluation scores in 10-point intervals.
2. **Scores by Category:** Box plots showing score variation across evaluation categories.
3. **Category Comparison:** Horizontal bar chart ranking categories by average score.

Interactive filters allow users to explore results by model version, category and date.

## Key Findings

| Category | Average Score |
|---|---:|
| Instruction Following | 72.21 |
| Knowledge | 65.98 |
| Code | 49.62 |
| Tool Calling | 48.35 |
| Reasoning | 40.85 |

Instruction Following has the highest average score, while Reasoning has the lowest. These results describe simulated data, not actual AI model performance.

## Data Source

**Option B — Generated Sample Evaluation Data** was selected.

The dataset was generated using Python, pandas and NumPy with the instructor-provided script. It contains 4,489 evaluation records with scores ranging from 0 to 100.

See [data_source.md](data_source.md) for details.

## Project Files

| File | Description |
|---|---|
| `instructions.md` | Original lab instructions |
| `rubric.md` | Assessment criteria |
| `generate_evaluation_data.py` | Python dataset generation script |
| `evaluation_data.csv` | Original generated dataset |
| `evaluation_data_clean.csv` | Dataset imported into Tableau |
| `evaluation_score_dashboard.twbx` | Packaged Tableau workbook |
| `dashboard_screenshot_top.png` | Upper dashboard and filters |
| `dashboard_screenshot_bottom.png` | Lower dashboard showing the box plots |
| `data_source.md` | Data source documentation |
| `reflection.md` | Reflection on dashboard communication and design |
| `lab_proof.md` | Reviewer entry point and execution evidence |

## Reproduction

Run the dataset generation script:

```bash
conda run -n bootcamp-env python generate_evaluation_data.py
```

The script requires pandas and NumPy.

The resulting CSV can be opened in Tableau Public. The packaged workbook contains the completed dashboard.

## Communication Layer

The dashboard focuses on what the evaluation results show and which categories may need attention. Statistical methodology, p-values and confidence intervals are excluded to keep the presentation accessible to non-technical stakeholders.

## Limitations

The dataset is synthetic. Results cannot establish actual model quality, production reliability or superiority between the named AI models.

## Submission

The completed lab must be committed to the forked GitHub repository, followed by a pull request to the original repository for AI review.

Only lab-related files should be included. No secrets, API keys or unrelated project files should be committed.