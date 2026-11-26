"""Step 1 (Option B): generate sample evaluation data. Script copied from the lab instructions, unchanged
except for the output path (data/evaluation_data.csv)."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "evaluation_data.csv"

# Set random seed for reproducibility
np.random.seed(42)

# Define evaluation categories
categories = ['reasoning', 'knowledge', 'code', 'instruction_following', 'tool_calling']

# Define model versions
model_versions = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus']

# Generate date range (last 90 days)
start_date = datetime.now() - timedelta(days=90)
dates = [start_date + timedelta(days=i) for i in range(90)]

# Generate evaluation data
data = []
evaluation_id = 1

for date in dates:
    for category in categories:
        # Generate 5-15 evaluations per category per day
        num_evaluations = np.random.randint(5, 16)

        for _ in range(num_evaluations):
            model = np.random.choice(model_versions)

            # Generate scores with category-specific distributions
            if category == 'reasoning':
                score = np.random.beta(2, 3) * 100      # lower scores, more variance
            elif category == 'knowledge':
                score = np.random.beta(4, 2) * 100      # higher scores
            elif category == 'code':
                score = np.random.beta(3, 3) * 100      # medium, high variance
            elif category == 'instruction_following':
                score = np.random.beta(5, 2) * 100      # high
            else:  # tool_calling
                score = np.random.beta(3, 3) * 100      # medium

            # Add some noise
            score = max(0, min(100, score + np.random.normal(0, 5)))

            data.append({
                'evaluation_id': evaluation_id,
                'category': category,
                'score': round(score, 2),
                'model_version': model,
                'date': date.strftime('%Y-%m-%d')
            })
            evaluation_id += 1

df = pd.DataFrame(data)
OUT.parent.mkdir(exist_ok=True)
df.to_csv(OUT, index=False)

print(f"Generated {len(df)} evaluation records")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("\nScore summary by category:")
print(df.groupby('category')['score'].describe())
print("\nFirst few rows:")
print(df.head())
