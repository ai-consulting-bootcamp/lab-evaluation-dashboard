# What Was Built

**LAB | Evaluation Dashboard** &mdash; Steps 4&ndash;11 and the optional extra
**Author:** Nnanyelugo Ahukannah
**Tool:** Tableau Public (web authoring)

A record of the workbook, sheet by sheet, so it can be checked or rebuilt without
opening it.

**Live workbook:**
https://public.tableau.com/app/profile/nnanyelugo.ahukannah/viz/evaluation_score_dashboard

## Data connections (Steps 3&ndash;4)

| Source | Rows | Grain |
|---|---|---|
| `evaluation_data_clean.csv` | 396 | one row per configuration x example x metric, plus an overall row per example |
| `judge_agreement.csv` | 76 | one row per graded item, automated-reviewer verdict beside rule-check verdict |

Both are packaged inside `evaluation_score_dashboard.twbx`, so the file opens
without the CSVs present.

## Worksheets

| # | Sheet | Shelves | Filter |
|---|---|---|---|
| 1 | **Score Distribution** | `Score` (discrete dimension) on Columns, `CNT(Evaluation Id)` on Rows, Bar marks | `Metric = Overall quality score` |
| 2 | **Score by Category** | `Category` + `Model Version` on Columns, `AVG(Score)` on Rows | `Metric = Overall quality score` |
| 3 | **Where Quality Breaks Down** | `Metric` + `Model Version` on Rows, `AVG(Score)` on Columns | `Metric` excludes the overall row, so the five component measures show |
| 4 | **Reviewer Agreement by Task** | `Task` on Columns, `AVG(Agreement)` on Rows | none |
| 5 | **Where They Disagreed** | `Disagreement Type` on Rows, `CNT(Evaluation Id)` on Columns | none |

Sheet 1 filters to the overall score deliberately. Every underlying metric is 0 or
1, so a distribution of the raw column is two bars; the overall row is the mean of
an example's five metrics and spreads across 0&ndash;100.

## Dashboards

**Dashboard 1 &mdash; evaluation quality.** Sheets 1&ndash;3, a text panel carrying
the headline in words, and two filter cards (`Model Version`, `Category`) as
tick-lists.

**Dashboard 2 &mdash; reviewer reliability (the optional extra).** Sheets 4&ndash;5
and a text panel explaining what agreement means without naming a method.

## What was deliberately left out

No p-values, confidence intervals, sample sizes, evaluator internals, token counts,
prompt text or raw model identifiers. Configurations are labelled *Premium model,
full instructions* / *Standard model, full instructions* / *Standard model, reduced
instructions*, and metrics read as *Answer is correct* or *Points to the right
source* rather than `correctness` or `citation_validity`. Those belong in the
analysis notebook.

Each chart is titled with the question it answers, and each dashboard states its
conclusion in a sentence rather than leaving the reader to derive it.
