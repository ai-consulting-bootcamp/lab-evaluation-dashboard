# Build guide: Tableau Desktop Public Edition (Mac)

Click-by-click steps for both dashboards. **Why** notes explain the consulting reasoning behind each choice.
Plan about 90 minutes for the main dashboard and 45 for the optional one.

> **Field names:** Tableau shows CSV columns in Title Case with spaces, so `category_label` appears as
> **Category Label**, `model_version` as **Model Version**, and so on. This guide uses those display names.

---

## 0. Setup (5 min)

1. Install **Tableau Desktop Public Edition** (free) from public.tableau.com → *Create* → *Download the app*. Sign in with a free Tableau Public account.
2. In Tableau: **File → New**. On the start page, under **Connect → To a File**, choose **Text file**.
3. Open `data/evaluation_data_clean.csv` from this folder.

---

# Dashboard 1: Model Evaluation Score Dashboard

## Step 4: Check the data connection (5 min)

On the **Data Source** tab, check the type icon above each column:

| Column | Icon should be | Fix if wrong |
|---|---|---|
| Evaluation Id | `#`, but used as a **dimension** | In the sheet, right-click → *Convert to Dimension* |
| Date | calendar | Click the icon → *Date* |
| Model Version, Category, Category Label, Score Band, Result | `Abc` | – |
| Score | `#` (a measure) | Click the icon → *Number (decimal)* |

Click **Sheet 1** at the bottom to start.

> **Why:** a wrong data type is the most common cause of a chart that "looks wrong". Checking now saves
> debugging later.

## Calculated fields (5 min)

Create these once and reuse them everywhere. **Analysis → Create Calculated Field…**

| Name | Formula | Format |
|---|---|---|
| `Pass Rate` | `SUM(IF [Result] = "Pass" THEN 1 ELSE 0 END) / COUNT([Evaluation Id])` | Right-click → Default Properties → Number Format → Percentage, 0 decimals |
| `Evaluations` | `COUNTD([Evaluation Id])` | Number, 0 decimals, thousands separator |
| `Date Range` | `STR(MIN([Date])) + " to " + STR(MAX([Date]))` | – |

> **Why:** *Pass Rate* translates a distribution into the question an executive actually asks: "how
> often is the model good enough?". The target of 70 is a business threshold we define and state on
> the dashboard. It is not a statistical test.

## Step 5: Score distribution histogram (15 min)

New sheet, named **Score Distribution**.
1. Drag **Score Band** to **Columns** and **Evaluations** to **Rows**. You get a bar chart.
2. Check that the bars run 0-9 … 90-100 left to right. If not: click the **Score Band** pill → *Sort* → *Alphabetic, Ascending*.
3. Drag **Result** to **Color**. Click Color → *Edit Colors*: Pass = dark green `#2E7D6B`, Below target = grey `#B0B7C3`.
4. Click the **Label** card → *Show mark labels* (counts on the bars).
5. Title (double-click the title area): **"Only 3 in 10 evaluations reach the target score of 70"**.
6. Axis titles: right-click the axes → *Edit Axis*. Columns: "Score (0-100)"; Rows: "Number of evaluations".

> **Why color by Result:** the eye immediately sees how much of the distribution sits below the target.
> The title states the conclusion (the "so what"), not just what the chart is.

## Step 6: Score distribution by category (20 min)

New sheet, named **Scores by Category**.
1. **Analysis → Aggregate Measures**: untick it. This turns off averaging, so every evaluation becomes a dot.
2. Drag **Category Label** to **Columns** and **Score** to **Rows**.
3. **Show Me** (top right) → choose **box-and-whisker plot**. If Show Me moves Category to Color or Detail, put it back on Columns.
4. Set the mark type to **Circle**, opacity about 20% (Color → Opacity), so the dots stay light and the boxes stand out.
5. Sort the categories by median: click the **Category Label** pill → *Sort* → *Field: Score, Median, Descending*.
6. Title: **"Reasoning is the weakest category; instruction following the strongest"**.
7. Add a caption: **Worksheet → Show Caption**, with this text:
   *"Each dot is one evaluation. The box shows where the middle half of the scores fall; the line inside is the typical score."*

> **Why the caption:** a box plot is a technical chart. One plain-language sentence makes it readable
> for a non-technical audience without using words like "quartile" or "IQR".
>
> **Turn Aggregate Measures back on** before building the next sheet (it applies to the whole workbook).

## Step 7: Category comparison (20 min)

New sheet, named **Category Comparison**.
1. Check that **Analysis → Aggregate Measures** is ticked again.
2. Drag **Category Label** to **Rows** and **Score** to **Columns**. Click the Score pill → *Measure* → *Average*.
3. Sort descending: hover the axis and click the sort icon, or use the toolbar **Sort Descending** button.
4. Color: drag **AVG(Score)** to **Color** → *Edit Colors* → palette **Red-Green Diverging**, tick *Use Full Color Range*, set *Center* to 55 (the overall average).
5. Label: drag **Pass Rate** onto **Label**, then add AVG(Score) too. Edit the label text to:
   `<AVG(Score)> avg  ·  <AGG(Pass Rate)> pass`
6. Reference line: **Analytics** pane (next to Data) → drag **Average Line** onto the chart → *Table*. Edit it: label = *Custom* "Overall average: <Value>"; line = dashed grey.
7. Title: **"Three of five categories score below the overall average of 55"**.

> **Why horizontal bars:** sorted horizontal bars are the fastest way for anyone to rank items, and
> the category names stay readable. The average line answers "compared to what?".

## Extra view: Does the model matter? (10 min, recommended)

New sheet, named **Model x Category**.
1. **Category Label** to Rows, **Model Version** to Columns, **AVG(Score)** to Color and to Label. Mark type: **Square**.
2. Use the same diverging palette as Category Comparison (centre 55).
3. Title: **"Category matters far more than model: all four models score within 3 points"**.

> **Why:** stakeholders will ask "which model should we use?". This heatmap answers in one glance: the
> rows differ, the columns barely do. (Note for us, not the dashboard: the sample generator assigns
> models at random, which explains this result. See `reflection.md`.)

## KPI cards (10 min)

Create four small sheets. In each, drag a measure onto **Text** in the Marks card, then format the text large (28-36 pt) with a small grey label underneath.

| Sheet name | Put on Text | Label text |
|---|---|---|
| KPI Evaluations | `Evaluations` | "evaluations" |
| KPI Average | `AVG(Score)` (format 0 decimals) | "average score (0-100)" |
| KPI Pass Rate | `Pass Rate` | "reach the target of 70" |
| KPI Period | `Date Range` | "evaluation period" |

## Step 8: Interactive filters (10 min)

On the **Category Comparison** sheet:
1. Right-click **Model Version** in the Data pane → **Show Filter**. Do the same for **Category Label** and **Date** (for Date choose *Range of Dates*).
2. For each filter card: click its dropdown → **Apply to Worksheets → All Using This Data Source**.
3. Card style: Model Version and Category Label → *Multiple Values (dropdown)*; Date → *Range of dates* slider.
4. Test: pick only `gpt-3.5-turbo`, then open the other sheets. Every chart and KPI should change.

> **Why "All Using This Data Source":** without it, a filter only affects one chart, and the dashboard
> shows inconsistent numbers. Executives lose trust fast when two charts disagree.

## Step 9: Dashboard layout (20 min)

1. **Dashboard → New Dashboard**. Size (left panel): **Fixed size → Custom, 1400 × 900**.
2. Layout, top to bottom:
   - **Row 1:** title text box: **"Model Evaluation Score Dashboard"**; subtitle: *"Performance by category and model version · scores from 0 to 100, where 100 is perfect"*.
   - **Row 2:** the four KPI sheets side by side (drag a *Horizontal* container first, then drop the sheets in it). Put the three filters at the right end of this row.
   - **Row 3:** **Category Comparison** (left, wide) and **Score Distribution** (right).
   - **Row 4:** **Scores by Category** (left) and **Model x Category** (right).
3. Hide the duplicate legends you don't need (click a legend → **x**). Keep the Result color legend next to the histogram.
4. **Filter action:** **Dashboard → Actions → Add Action → Filter…** Source sheet: *Category Comparison*; run on: *Select*; target: all other sheets; clearing the selection: *Show all values*. Now clicking a category bar filters the whole dashboard.
5. Add a small text box at the bottom: *"Use the filters at the top right, or click a category bar, to explore. Target: a score of 70 or above counts as a pass."*

> **Why this order:** headline numbers first (KPIs), then *where* the problem is (category ranking), then
> *how* scores spread (distribution), then detail. Readers go from conclusion to evidence, the
> communication-layer principle from the lesson.

## Step 10-11: Polish, test, save, screenshot (15 min)

- **Remove clutter:** for each sheet, *Format → Lines → Grid Lines: None*, and drop axis titles that repeat the chart title.
- **Plain language:** no "mean", "median", "variance" or "distribution" in titles. Tooltips: edit them to read, e.g., *"Reasoning · average score 41 · 9% reach the target"*.
- **Test:** click every filter option and a category bar, then *Reset*. Check that the KPIs change with the filters.
- **Save:** **File → Save As…** → format **Tableau Packaged Workbook (.twbx)** → `evaluation_score_dashboard.twbx` in this folder.
- **Screenshot:** **Dashboard → Export Image…** → `dashboard_screenshot.png` (or Cmd+Shift+4 on the Mac).

---

# Dashboard 2 (optional extra): Judge Agreement Analysis

Open a **new workbook** (File → New) and connect to `data/judge_agreement_data.csv`.

The data has 72 rows: pairs of runs of the **same** LLM judge on the same letter, from my LLM Judges lab, with judge prompt v1 (before the fix) and v2 (after). Scores are on 0-100. **Agreement = the two runs are within 25 points (one step on the judge's 1-5 scale).**

### Calculated fields

| Name | Formula | Format |
|---|---|---|
| `Agreement Rate` | `AVG([Agreement])` | Percentage, 0 decimals |
| `Pairs Compared` | `COUNT([Evaluation Id])` | Number |

### Step 2: Agreement rate by category

New sheet, named **Agreement by Category**.
1. **Category** to Rows, **Agreement Rate** to Columns, **Judge Prompt Version** to **Color** *and* to Rows (to the right of Category). You get side-by-side bars, v1 vs v2, per category.
2. Colors: v1 (before fix) = grey `#B0B7C3`, v2 (after fix) = green `#2E7D6B`. Labels on.
3. Title: **"After the prompt fix, the judge gives consistent scores in every category"**.

### Step 3: Agreement distribution

New sheet, named **Score Differences**.
1. Right-click **Score Difference** → *Convert to Dimension* (it only takes the values 0, 25, 50, 75). Drag it to **Columns**.
2. **Pairs Compared** to Rows, **Judge Prompt Version** to Color, and also to Columns (left of Score Difference) for side-by-side panels.
3. Title: **"With v2, repeated runs give the same score; with v1, some repeated runs were 75 points apart"**.

### Step 4: Judge comparison scatter plot

New sheet, named **Run vs Run**.
1. **Analysis → Aggregate Measures**: untick. **Judge 1 Score** to Columns, **Judge 2 Score** to Rows.
2. Because scores take only five values, many dots sit on top of each other. Fix that: drag **Pairs Compared** to **Size** (turn Aggregate Measures back on first; the Size marks then show how many pairs sit on each point). Mark type: **Circle**.
3. **Judge Prompt Version** to Color (same colors as before).
4. **Analytics → Trend Line** → Linear.
5. Caption: *"Each circle is a pair of judge runs; bigger circles = more pairs. Points on the diagonal mean both runs gave the same score."*

### Step 5: Combine into a dashboard

1. **Dashboard → New Dashboard**, fixed 1400 × 900, title **"Judge Agreement Analysis Dashboard"**.
2. KPI row: **Agreement Rate** (format big), **AVG(Score Difference)** ("average gap, in points"), **Pairs Compared**.
   Add **Judge Prompt Version** and **Category** as filters (Apply to all worksheets using this data source).
3. Layout: Agreement by Category (left, wide), Score Differences (right), Run vs Run (bottom).
4. Context text box: *"This dashboard shows how consistently our AI judge scores the same letter when it runs three times. Agreement = runs within 25 points (one step on the judge's 1-5 scale). Higher agreement means more reliable evaluation results. Source: W7D4 LLM Judges lab (gpt-5.4-mini judge, 12 letters × 3 runs × 2 prompt versions)."*
5. Save as `judge_agreement_dashboard.twbx`; export the image as `judge_agreement_screenshot.png`.

**Expected headline numbers** (to check your build): v1 agreement **78%**, average gap **19.4** points · v2 agreement **100%**, average gap **1.4** points.
