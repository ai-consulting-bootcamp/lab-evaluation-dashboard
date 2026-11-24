# Lab Proof — Evaluation Score Distribution Dashboard

## 1. Objective

Build an interactive, stakeholder-oriented dashboard in Tableau that communicates evaluation score distributions and category-level performance without requiring the audience to interpret statistical tests or Python notebooks.

## 2. Implementation and workflow

- **BI tool:** Tableau Public (browser-based authoring)
- **Data preparation:** Python, pandas and NumPy in VS Code (`bootcamp-env`)
- **Data source:** Option B — synthetic evaluation data, based on the sample generator provided in the lab instructions
- **Reproducibility:** NumPy random seed `42`; the date range is relative to the execution date.

Workflow: generate and validate data → export CSV → import into Tableau → create three worksheets → configure shared filters → assemble and format the dashboard.

### Supporting files

| File | Purpose |
|---|---|
| [generate_evaluation_data.py](./generate_evaluation_data.py) | Data generation and validation code |
| [evaluation_data.csv](./evaluation_data.csv) | Raw generated dataset |
| [evaluation_data_clean.csv](./evaluation_data_clean.csv) | Validated Tableau data source |
| [evaluation_score_dashboard.twbx](./evaluation_score_dashboard.twbx) | Expected packaged Tableau workbook for submission |
| [dashboard_screenshot.png](./dashboard_screenshot.png) | Expected final dashboard image for submission |
| [data_source.md](./data_source.md) | Data source documentation |
| [reflection.md](./reflection.md) | Reflection on dashboard design and limitations |

## 3. Run evidence

Executed on November 24, 2026, in the local lab repository:

```powershell
conda activate bootcamp-env
python generate_evaluation_data.py
```

**Input:** No external input file or API was required. The script uses a fixed random seed, five evaluation categories, four randomly assigned model labels, category-specific beta distributions, additional random noise and a 90-day date window.

**Observed output (terminal excerpt):**

```text
DATA GENERATION SUCCESSFUL
----------------------------------------
Total evaluations: 4489
Categories: 5
Models: 4
Date range: 2026-08-26 to 2026-11-23
Missing values: 0
Duplicate IDs: 0
Overall average score: 55.33

Average scores by category:
category
instruction_following    72.21
knowledge                65.98
code                     49.62
tool_calling             48.35
reasoning                40.85
Name: score, dtype: float64

All validation checks passed.
Created: evaluation_data.csv
Created: evaluation_data_clean.csv
```

The script checks that the dataset contains at least 100 records, unique evaluation IDs, numerical scores within 0–100, valid category labels and parseable dates. The reported run contained no missing values or duplicate IDs.

## 4. Tableau implementation and output

Tableau Public successfully recognized all 4,489 records and five fields: `Evaluation Id`, `Category`, `Score`, `Model Version` and `Date`.

| Worksheet | Implementation | Stakeholder question |
|---|---|---|
| Score Distribution | Histogram with 10-point score bins and count of scores | How frequently do low, medium and high scores occur? |
| Scores by Category | Box plots based on individual evaluation IDs | How much do scores vary within each category? |
| Category Comparison | Horizontal bar chart using average score, sorted descending, with average-score labels | Which categories perform best and which need attention? |

The three worksheets were assembled into the **Model Evaluation Score Dashboard**. The dashboard uses a fixed 1,200 × 800 layout, a descriptive title, a synthetic-data notice, a score-scale explanation and a written key takeaway. Model Version, Category and Date filters are visible in the dashboard.

### Observed results — full synthetic dataset

| Category | Average score (0–100) |
|---|---:|
| Instruction following | 72.21 |
| Knowledge | 65.98 |
| Code | 49.62 |
| Tool calling | 48.35 |
| Reasoning | 40.85 |

Overall average score: **55.33/100**.

**Stakeholder takeaway:** Instruction following has the highest average score, while reasoning has the lowest and is the main simulated improvement opportunity. These findings describe the generated dataset only; they do not establish actual model quality or justify a production model switch.

### Verification status

| Check | Status |
|---|---|
| Data generation and validation | Passed — terminal output |
| CSV import and field recognition | Verified — Tableau data source view |
| Three visualizations and dashboard layout | Verified — Tableau screenshots |
| Category averages match Python output | Verified — Tableau labels match terminal results |
| Model, category and date filter controls present | Verified — dashboard screenshot |
| All three filters update every intended worksheet | Final interaction test not independently confirmed |
| Cross-filtering via chart selection and reset | Final interaction test not independently confirmed |
| Packaged workbook and final image saved locally | Local export not independently confirmed |

Before submitting, verify the remaining interaction and export checks and ensure the linked workbook and screenshot are present in the repository.

## 5. Failure encountered and limitation

During the initial creation of the category comparison chart, the bars used `AVG(Score)` but their labels used `SUM(Score)`. This produced misleading labels even though the bar lengths were correct. Changing the label aggregation to `AVG(Score)` resolved the discrepancy. The displayed category averages then matched the Python validation output.

A further limitation is that the evaluation data is synthetic. Model labels are assigned randomly, and scores are generated according to category-specific distributions rather than measured model performance. The dashboard is therefore a demonstration of the communication layer and cannot be used to rank real AI models. The script also uses a relative date window, so rerunning it on another day changes the date range.

## 6. Scope

The dashboard focuses on the required core lab. The optional Judge Agreement Dashboard was not implemented. No p-values, confidence intervals or statistical test details are included in the stakeholder view.
