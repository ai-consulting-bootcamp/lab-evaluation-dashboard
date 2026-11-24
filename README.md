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

## How each visualization was built (Tableau)

### Step 5: Score Distribution Histogram (sheet "Score Distribution")
- Created bins on `Score` (Create → Bins, bin size 10), renamed to "Score range (0–100)"
- Columns: Score range (bin) · Rows: CNT(evaluation_data_clean.csv), axis renamed "Number of evaluations"
- Title: "Score Distribution: how often each score range occurs"
- Insight: most scores fall between 30 and 80; very few at 0–10 or 90–100

### Step 6: Score Distribution by Category (sheet "Scores by Category")
- Box plot: Columns: Category · Rows: Score, with Aggregate Measures turned off (one dot per evaluation)
- Marks: Circle, small size, 30% opacity; Analytics pane → Box Plot added per cell
- Categories sorted by median score, ascending; axis "Score (0–100, higher = better)"
- Insight: Reasoning has the lowest median and the widest spread; Instruction Following is highest and most consistent

### Step 7: Category Comparison Chart (sheet "Category Comparison")
- Horizontal bar chart: Rows: Category · Columns: AVG(Score), sorted descending
- Labels show the average with 1 decimal; colour = AVG(Score) blue gradient (lighter = weaker)
- Average Line (Analytics pane) shows the overall average (~55)
- Result: Instruction Following 72.2 · Knowledge 66.0 · Code 49.6 · Tool Calling 48.3 · Reasoning 40.8

### Step 8: Interactive Filters
- **Model Version** (multi-select checkboxes), **Category** (checkboxes), **Date** (range slider, 26 Aug – 23 Nov 2026)
- Each filter set to *Apply to Worksheets → Selected Worksheets* with all three sheets ticked
- Tested: selecting only GPT-3.5 Turbo, or unticking Reasoning, updates all three charts

### Dashboard layout (Steps 9–10)
- Title "Model Evaluation Score Dashboard" at the top
- Left: Category Comparison (top), a text box with "What this shows / Key takeaway / Use the filters" (middle), Score Distribution histogram (bottom)
- Right: colour legend, Scores by Category box plot, then the three filters
- Size: Automatic (fits the screen)

### Testing checklist (Step 11)
- [x] All three filters update all three charts
- [x] Titles and axis labels use plain language, no raw field names
- [x] Key takeaway text is visible on the dashboard
- [x] Dashboard fits on one screen; no overlapping elements
- [x] Fixed after testing: box plot was too narrow (widened); text box overlapped an axis (moved); one chart lost its data connection and was rebuilt on the re-uploaded CSV

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