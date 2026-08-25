# Data dictionary

## `evaluation_data_clean.csv`

| Field | Type | Definition |
| --- | --- | --- |
| `evaluation_id` | Integer | Unique evaluation record identifier. |
| `category` | Text | Evaluation category: reasoning, knowledge, code, instruction following, or tool calling. |
| `score` | Decimal | Evaluation score on a 0–100 scale. |
| `model_version` | Text | Fictional assistant version used for comparison. |
| `date` | Date | Evaluation date in `YYYY-MM-DD` format. |
| `score_band` | Text | Stakeholder-friendly status: Needs improvement (<60), Watch (60–79.99), or Strong (≥80). |
| `score_bin` | Integer | Lower bound of the 10-point score bin used in the histogram. |

## `judge_agreement_data.csv`

| Field | Type | Definition |
| --- | --- | --- |
| `evaluation_id` | Integer | Unique paired-evaluation identifier. |
| `category` | Text | Shared evaluation category. |
| `judge_1_score` | Decimal | First judge score on a 0–100 scale. |
| `judge_2_score` | Decimal | Second judge score on a 0–100 scale. |
| `score_difference` | Decimal | Absolute difference between the two judge scores. |
| `difference_bin` | Integer | Lower bound of the five-point difference bin. |
| `agreement` | Integer | `1` when the absolute difference is at most 10 points; otherwise `0`. |
| `date` | Date | Evaluation date in `YYYY-MM-DD` format. |

## Cleaning and validation

- Scores are numeric and constrained to 0–100.
- Category and model labels are standardized before export.
- Dates use one consistent ISO format.
- Critical fields contain no missing values.
- The agreement indicator is derived from one visible, reproducible threshold.

