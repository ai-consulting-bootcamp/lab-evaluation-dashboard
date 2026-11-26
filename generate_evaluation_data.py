"""Generate the sample evaluation datasets for the dashboard (lab Option B).

Writes two raw CSVs:
  evaluation_data.csv       - one row per evaluation: category, score (0-100), model, date
  judge_agreement_data.csv  - one row per evaluation scored by two judges (optional extra)

The generators are the ones given in instructions.md, with one change: the 90-day
window ends on a fixed date (END_DATE) instead of datetime.now(), so the CSVs are
identical on every run. The seed and RNG call order are unchanged.
"""
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

END_DATE = datetime(2026, 11, 26)
CATEGORIES = ['reasoning', 'knowledge', 'code', 'instruction_following', 'tool_calling']
MODEL_VERSIONS = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus']

# Category-specific Beta(a, b) shapes, scaled to 0-100 (from the lab spec)
BETA_PARAMS = {
    'reasoning': (2, 3),              # lower, more variance
    'knowledge': (4, 2),              # higher
    'code': (3, 3),                   # medium, high variance
    'instruction_following': (5, 2),  # high
    'tool_calling': (3, 3),           # medium
}


def date_range():
    start = END_DATE - timedelta(days=90)
    return [start + timedelta(days=i) for i in range(90)]


def generate_evaluations():
    np.random.seed(42)
    rows, eid = [], 1
    for date in date_range():
        for category in CATEGORIES:
            for _ in range(np.random.randint(5, 16)):
                model = np.random.choice(MODEL_VERSIONS)
                a, b = BETA_PARAMS[category]
                score = np.random.beta(a, b) * 100
                score = max(0, min(100, score + np.random.normal(0, 5)))
                rows.append({'evaluation_id': eid, 'category': category,
                             'score': round(score, 2), 'model_version': model,
                             'date': date.strftime('%Y-%m-%d')})
                eid += 1
    return pd.DataFrame(rows)


def generate_judge_agreement():
    np.random.seed(42)
    rows, eid, correlation = [], 1, 0.75
    for date in date_range():
        for category in CATEGORIES:
            for _ in range(np.random.randint(3, 10)):
                base = np.random.beta(3, 3) * 100
                j1 = max(0, min(100, base + np.random.normal(0, 8)))
                j2 = max(0, min(100, base * correlation
                                + (1 - correlation) * np.random.beta(3, 3) * 100
                                + np.random.normal(0, 8)))
                rows.append({'evaluation_id': eid, 'category': category,
                             'judge_1_score': round(j1, 2), 'judge_2_score': round(j2, 2),
                             'score_difference': round(abs(j1 - j2), 2),
                             'agreement': int(abs(j1 - j2) <= 10),
                             'date': date.strftime('%Y-%m-%d')})
                eid += 1
    return pd.DataFrame(rows)


if __name__ == '__main__':
    evals = generate_evaluations()
    evals.to_csv('evaluation_data.csv', index=False)
    print(f"evaluation_data.csv: {len(evals)} rows, {evals['date'].min()} to {evals['date'].max()}")
    print(evals.groupby('category')['score'].describe().round(1))

    judges = generate_judge_agreement()
    judges.to_csv('judge_agreement_data.csv', index=False)
    print(f"\njudge_agreement_data.csv: {len(judges)} rows, "
          f"agreement rate {judges['agreement'].mean():.1%}")
    print(judges.groupby('category')['agreement'].mean().round(3))
