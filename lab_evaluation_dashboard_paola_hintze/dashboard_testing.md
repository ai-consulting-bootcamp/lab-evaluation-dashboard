# Dashboard testing and rubric evidence

## Functional checks

- [x] Tableau workbook XML parses successfully.
- [x] Packaged workbooks contain their referenced CSV files.
- [x] The core dataset contains more than 100 rows (1,800 records).
- [x] Score, category, model, and date fields contain no critical null values.
- [x] Scores remain within the 0–100 range.
- [x] Category labels are consistent across both datasets.
- [x] Model, category, and date controls are declared in the main Tableau dashboard.
- [x] Category and date controls are declared in the judge agreement dashboard.
- [x] A category selection action targets the remaining core dashboard views.
- [x] The offline HTML filters and category click-to-filter interaction update every applicable view.

## Visual checks

- [x] Core screenshot includes score distribution, category distribution, ranked category comparison, and model comparison.
- [x] Judge screenshot includes agreement rate, score-difference distribution, and judge comparison scatter plot.
- [x] Titles, axes, labels, and KPI values are legible at 16:9 resolution.
- [x] Color is used consistently: teal for stronger performance and coral for improvement priorities.
- [x] No statistical jargon appears in stakeholder-facing views.

## Rubric coverage

| Rubric requirement | Evidence |
| --- | --- |
| Connect data to Tableau | Two CSV connections are embedded in the packaged workbooks. |
| At least three visualizations | Four core views plus three judge agreement views. |
| Interactive filters | Model, category, and date filters; category selection action. |
| Non-technical stakeholder design | KPI-first layout, plain-language titles, restrained color, and explanatory subtitles. |
| Communication layer | Dashboard answers “what” and “so what”; methods remain in the generator and documentation. |
| Judge agreement extension | Agreement rate, difference distribution, scatter plot, three KPIs, and two filters. |

