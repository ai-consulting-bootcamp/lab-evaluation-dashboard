# ShopCo Evaluation Dashboard

This lab uses Tableau Public to present 300 synthetic ShopCo evaluation records. The dashboard includes a score histogram, average scores by category, and a comparison of two fictional versions.

Category and version filters update all three charts. The scores are simulated and do not measure real agent performance.

## Review

Start with [lab_proof.md](lab_proof.md) for the workflow, evidence, results, and limitations.

[Open the interactive dashboard](https://public.tableau.com/views/ShopCoEvaluationDashboard-SyntheticData/ShopCoDashboard?:showVizHome=no)

## Files

| File | Purpose |
|---|---|
| lab_proof.md | Main evidence and workflow |
| generate_shopco_data.py | Generates and validates the synthetic data |
| evaluation_data_clean.csv | Dataset used in Tableau |
| [evaluation_score_dashboard.twbx](evaluation_score_dashboard.twbx) | Editable Tableau packaged workbook |
| dashboard_screenshot.png | Image of the complete dashboard |
| data_source.md | Data source and reason for using synthetic data |

## Generate the data

With Python and pandas installed, run:

python generate_shopco_data.py

The script saves evaluation_data_clean.csv in the same folder.

## Scope

The optional judge agreement dashboard was not completed.