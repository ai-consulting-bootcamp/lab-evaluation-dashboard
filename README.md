# Evaluation Score Distribution Dashboard

**Tool used:** Tableau Public (web authoring)

**Live dashboard:** [(https://public.tableau.com/app/profile/barsha.mishra1113/viz/ModelEvaluationScoreDashboard_17955355694690/Dashboard1)]

![Dashboard screenshot](dashboard_screenshot.png)

## Overview
An interactive dashboard that communicates AI model evaluation results to a non-technical audience. It answers three questions:
1. **Category Comparison:** which task types score highest and lowest on average (sorted bar chart with an overall-average reference line)
2. **Score Distribution:** how scores are spread overall (histogram, bins of 10)
3. **Scores by Category:** how consistent each task type is (box plot)

Filters for **Model Version**, **Category** and **Date** apply to all three charts.

**Key takeaway:** Instruction Following (~72) and Knowledge (~66) are strengths. Reasoning (~41) is the weakest area and the top priority for improvement.

## Data notes
- Generated sample data (Option B) from the lab's script, 4,489 evaluations, 26 Aug – 23 Nov 2026
- Cleaned with `clean_evaluation_data.py`: no missing or out-of-range values; readable category and model labels
- Details in [data_source.md](data_source.md)

## Files
| File | Description |
|---|---|
| `evaluation_score_dashboard.twbx` | Tableau packaged workbook |
| `dashboard_screenshot.png` | Screenshot of the final dashboard |
| `generate_evaluation_data.py` | Generates the sample data |
| `clean_evaluation_data.py` | Cleans the data for Tableau |
| `evaluation_data.csv` / `evaluation_data_clean.csv` | Raw and cleaned data |
| `data_source.md` | Data source explanation |
| `reflection.md` | Design choices and reflection |

*The optional judge-agreement dashboard was not completed.*