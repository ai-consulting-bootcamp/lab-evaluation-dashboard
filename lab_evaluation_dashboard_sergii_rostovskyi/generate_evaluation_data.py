from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Define evaluation categories
categories = ['reasoning', 'knowledge', 'code', 'instruction_following', 'tool_calling']

# Define model versions
model_versions = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'claude-3-opus']

# Generate date range (90 complete days ending on November 24, 2026)
start_date = date(2026, 11, 25) - timedelta(days=90)
dates = [start_date + timedelta(days=i) for i in range(90)]
output_dir = Path(__file__).resolve().parent

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
                # Reasoning tends to have lower scores, more variance
                score = np.random.beta(2, 3) * 100
            elif category == 'knowledge':
                # Knowledge tends to have higher scores
                score = np.random.beta(4, 2) * 100
            elif category == 'code':
                # Code has medium scores with high variance
                score = np.random.beta(3, 3) * 100
            elif category == 'instruction_following':
                # Instruction following tends to be high
                score = np.random.beta(5, 2) * 100
            else:  # tool_calling
                # Tool calling has medium scores
                score = np.random.beta(3, 3) * 100

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

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv(output_dir / 'evaluation_data.csv', index=False, encoding='utf-8')

required_fields = ['evaluation_id', 'category', 'score', 'model_version', 'date']
clean_data = df.dropna(subset=required_fields)
clean_data.to_csv(output_dir / 'evaluation_data_clean.csv', index=False, encoding='utf-8')

print(f"Generated {len(df)} evaluation records")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print("\nScore summary by category:")
print(df.groupby('category')['score'].describe())
print("\nFirst few rows:")
print(df.head())
