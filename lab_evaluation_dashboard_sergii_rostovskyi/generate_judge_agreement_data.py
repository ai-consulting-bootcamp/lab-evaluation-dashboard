from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

np.random.seed(42)

categories = ['reasoning', 'knowledge', 'code', 'instruction_following', 'tool_calling']
# The sample covers 90 complete days ending on November 24, 2026.
start_date = date(2026, 11, 25) - timedelta(days=90)
dates = [start_date + timedelta(days=i) for i in range(90)]
output_dir = Path(__file__).resolve().parent

data = []
evaluation_id = 1

for date in dates:
    for category in categories:
        num_evaluations = np.random.randint(3, 10)

        for _ in range(num_evaluations):
            # Generate base score
            base_score = np.random.beta(3, 3) * 100

            # Judge 1 score (with some variance)
            judge_1_score = max(0, min(100, base_score + np.random.normal(0, 8)))

            # Judge 2 score (correlated with judge 1, but with variance)
            # Higher correlation = better agreement
            correlation = 0.75  # Adjust for different agreement levels
            judge_2_score = max(0, min(100,
                base_score * correlation + (1 - correlation) * np.random.beta(3, 3) * 100 + np.random.normal(0, 8)))

            # Compute agreement from the scores recorded in the CSV.
            judge_1_score = round(judge_1_score, 2)
            judge_2_score = round(judge_2_score, 2)
            score_difference = round(abs(judge_1_score - judge_2_score), 2)
            agreement = int(score_difference <= 10)

            data.append({
                'evaluation_id': evaluation_id,
                'category': category,
                'judge_1_score': judge_1_score,
                'judge_2_score': judge_2_score,
                'score_difference': score_difference,
                'agreement': agreement,
                'date': date.strftime('%Y-%m-%d')
            })
            evaluation_id += 1

df = pd.DataFrame(data)
df.to_csv(output_dir / 'judge_agreement_data.csv', index=False, encoding='utf-8')

print(f"Generated {len(df)} judge agreement records")
print(f"\nAgreement rate: {df['agreement'].mean():.2%}")
print(f"\nAgreement by category:")
print(df.groupby('category')['agreement'].mean())
