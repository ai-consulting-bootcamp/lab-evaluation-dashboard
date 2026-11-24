# Lab Proof: ShopCo Evaluation Dashboard

## Objective

Build an interactive dashboard that presents evaluation scores in clear language for non-technical stakeholders.

## Data and input

I used 300 synthetic records across five ShopCo support categories and two fictional versions. Each category and version combination contains 30 records.

The scores range from 0 to 100. They were generated for dashboard practice and were not measured from agent responses.

- [Data source](data_source.md)
- [Input CSV](evaluation_data_clean.csv)
- [Python script](generate_shopco_data.py)

## Workflow

1. Generate synthetic scores with Python and random seed 42.
2. Validate record count, unique IDs, missing values, score range, and group sizes.
3. Import the CSV into Tableau Public.
4. Create a histogram with 10-point score intervals.
5. Create a bar chart with average scores by category.
6. Create a bar chart comparing the two fictional versions.
7. Add category and version filters to all three charts.
8. Add clear titles and a note explaining the synthetic data.
9. Test the filters and publish the dashboard.

## Run and evidence

Command:

`python generate_shopco_data.py`

Observed output:

- Rows: 300
- Data source: synthetic
- Validation checks passed.

The script checks that each category and version combination has 30 records. It also checks that scores are between 0 and 100, IDs are unique, and no values are missing.

## Interaction checks

| Input selection | Observed result |
|---|---|
| ShopCo_v1, all categories | All three charts updated. Delivery averaged 81.30 and Ambiguous requests averaged 59.07. |
| Both versions, Ambiguous requests | All three charts updated. The category average was 61.99. Version averages were 59.07 for v1 and 64.90 for v2. |
| Both versions, all categories | The dashboard displayed five category averages and ten version comparison bars. |

## Final output

- [Interactive dashboard](https://public.tableau.com/views/ShopCoEvaluationDashboard-SyntheticData/ShopCoDashboard?:showVizHome=no)
- [Tableau workbook](evaluation_score_dashboard.twbx)
- [Dashboard image](dashboard_screenshot.png)

![ShopCo synthetic evaluation dashboard](dashboard_screenshot.png)

## Findings in the simulated data

Delivery had the highest category average at 84.42. Ambiguous requests had the lowest average at 61.99.

The fictional v2 had higher average scores in every category. These patterns reflect the data generation assumptions and random variation. They do not prove real improvements in ShopCo.

In a real evaluation, these views could help identify categories for further testing before making decisions.

## Communication choices

I used plain English titles, visible values, and fixed 0–100 axes for the average score charts. Blue and orange distinguish the two fictional versions.

The dashboard explains the data source and score scale. Statistical methods and validation details remain in the supporting files.

## Failure and correction

I first created a manual score group instead of numeric intervals. This produced many small bars for individual score values. I replaced it with 10-point intervals to create the histogram.

A category chart also hid one category behind a scrollbar. I adjusted the view so all five categories were visible.

## Limitations

The dataset contains simulated scores without actual questions, agent responses, or judge evaluations. It cannot measure real accuracy or support a deployment decision.

Scores above 100 or below 0 were clipped to the allowed range. The histogram therefore includes a separate bin for scores exactly equal to 100.

## AI assistance

I used ChatGPT to help write the data generation script, explain Tableau steps, and draft documentation. I ran the script and built and tested the dashboard in Tableau.

## Optional work

The optional judge agreement dashboard was not completed.