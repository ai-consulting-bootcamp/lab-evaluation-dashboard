# LAB | Evaluation Dashboard

Week 8 of the Ironhack AI Consulting Bootcamp &mdash; turning evaluation results
into something a non-technical stakeholder can read and interrogate.
**Author:** Nnanyelugo Ahukannah
**Tool:** Tableau Public

Fork of [`ai-consulting-bootcamp/lab-evaluation-dashboard`](https://github.com/ai-consulting-bootcamp/lab-evaluation-dashboard).
`instructions.md` and `rubric.md` are unchanged; the original lab README is
preserved in full below this section.

## Live dashboards

**https://public.tableau.com/app/profile/nnanyelugo.ahukannah/viz/evaluation_score_dashboard**

- **Dashboard 1** &mdash; evaluation quality: score distribution, score by category, and where quality breaks down, with Model Version and Category filters
- **Dashboard 2** &mdash; reviewer reliability (the optional extra): agreement by task, and where the two reviewers disagreed

## Data source

**Option A &mdash; real results from my own earlier evaluation work**, not the
generated sample data. 396 rows from a three-configuration LangSmith experiment
over a 22-question compliance corpus scored by five evaluators, plus 76 rows
pairing an automated reviewer's verdict against a deterministic rule check on the
same items. `prepare_dashboard_data.py` reshapes both; see
[`data_source.md`](lab_evaluation_dashboard_ugo_ahukannah/data_source.md).

All underlying data is fictional &mdash; the client, corpus and letters were
authored for a teaching exercise.

## What the dashboards show

**Cutting the instructions given to the model leaves answers still looking correct
while the sources behind them stop being checkable.** The reduced-instruction
configuration averages 58 against 94 for the same model with full instructions,
and the gap is almost entirely in whether an answer points at a source a reviewer
could actually look up.

**The two reviewers agree 92% of the time on routine questions and 10% on the
regulated letters.** Where they disagree it is nearly always the automated reviewer
passing something the rule check rejected &mdash; which is the direction that
matters, because that is the one that reaches a customer.

## File map

| Path | What it is |
|---|---|
| `lab_evaluation_dashboard_ugo_ahukannah/evaluation_score_dashboard.twbx` | The Tableau workbook &mdash; 5 worksheets, 2 dashboards, both data sources packaged |
| `lab_evaluation_dashboard_ugo_ahukannah/dashboard_screenshot.png` | Dashboard 1 as published |
| `lab_evaluation_dashboard_ugo_ahukannah/judge_agreement_dashboard.twbx` | The optional extra's workbook file. **Byte-identical to the file above** &mdash; Tableau Public keeps both dashboards in one workbook, so this is the same packaged file under the filename the brief names for the extra. |
| `lab_evaluation_dashboard_ugo_ahukannah/judge_agreement_screenshot.png` | Dashboard 2 as published |
| [`data_source.md`](lab_evaluation_dashboard_ugo_ahukannah/data_source.md) | Step 1 &mdash; which data, from where, and how it was reshaped |
| [`dashboard_build_spec.md`](lab_evaluation_dashboard_ugo_ahukannah/dashboard_build_spec.md) | Steps 4&ndash;11 &mdash; every sheet, shelf, filter and dashboard zone |
| [`reflection.md`](lab_evaluation_dashboard_ugo_ahukannah/reflection.md) | Communication-layer reflection: what was included, excluded, and what I would change |
| `lab_evaluation_dashboard_ugo_ahukannah/prepare_dashboard_data.py` | Builds both CSVs from the raw evaluation runs, with the checks stated |
| `lab_evaluation_dashboard_ugo_ahukannah/evaluation_data_clean.csv` | 396 rows &mdash; the main dataset |
| `lab_evaluation_dashboard_ugo_ahukannah/judge_agreement.csv` | 76 rows &mdash; reviewer agreement |

## Rubric coverage

| Rubric rows | Where |
|---|---|
| 1, 7, 15 &mdash; connect data to the BI tool | Two CSVs connected in Tableau Public; packaged in the `.twbx` |
| 2, 8, 16&ndash;18 &mdash; score distributions and category views | Sheets *Score Distribution*, *Score by Category*, *Where Quality Breaks Down* |
| 3, 9, 19 &mdash; interactive filters | Model Version and Category filter cards on Dashboard 1 |
| 4, 10, 20&ndash;22 &mdash; stakeholder-ready dashboard | Two dashboards, plain-English labels, titles phrased as questions, context sentence each |
| 5, 11 &mdash; communication-layer principles | [`reflection.md`](lab_evaluation_dashboard_ugo_ahukannah/reflection.md) and the "deliberately left out" section of the build spec |
| 6 &mdash; dashboard versus notebook | Same section; the evaluator internals stayed in the notebook |
| 12&ndash;14 &mdash; data source, cleaning, preparation | [`data_source.md`](lab_evaluation_dashboard_ugo_ahukannah/data_source.md), `prepare_dashboard_data.py` |
| 23&ndash;27 &mdash; *(optional)* judge agreement | Dashboard 2, both agreement sheets, `judge_agreement.csv` |

The optional extra is complete.

## Interaction check

The published filters were tested rather than assumed: unchecking *Standard model,
reduced instructions* on Dashboard 1 removes it from the category and metric
charts (its axis labels drop from five occurrences to one, the remaining one being
the filter card itself) and the charts re-render. The filter was restored
afterwards, so the published default shows all configurations.

## Rebuilding the data

```bash
cd lab_evaluation_dashboard_ugo_ahukannah
python prepare_dashboard_data.py     # rewrites both CSVs and prints its checks
```

It reads the earlier runs read-only and never modifies them. No API keys are
needed and none are stored in this repository.

---
---

# Original lab README

*Everything below is unmodified from the upstream lab repository.*

# Evaluation Dashboard

**Track:** Module 5 — Evaluation & strategy · **When:** Week 8, Day 2 · **Status:** Required

This repository contains everything you need for this lab.

## Files

- [`instructions.md`](./instructions.md) — the lab instructions
- [`rubric.md`](./rubric.md) — how your submission is graded; this is what the AI reviewer checks your PR against

## How to complete this lab

1. **Fork** this repository.
2. Do the work described in `instructions.md`, committing to your fork.
3. Open a **pull request** back into this repository.
4. You'll receive **AI feedback** on your PR based on `rubric.md`. Address any blocking feedback and push updates to the same PR.

## Submission hygiene

- Keep this repository scoped to this lab only — no unrelated projects or personal files.
- Use clear, descriptive filenames.
- Remove secrets, API keys, and tokens before committing.
