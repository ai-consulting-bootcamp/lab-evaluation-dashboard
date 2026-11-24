
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Reproducibility
np.random.seed(42)

# Evaluation categories
categories = [
    "reasoning",
    "knowledge",
    "code",
    "instruction_following",
    "tool_calling"
]

# Model versions
model_versions = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "claude-3-opus"
]

# Category-specific score distributions
distributions = {
    "reasoning": (2, 3),
    "knowledge": (4, 2),
    "code": (3, 3),
    "instruction_following": (5, 2),
    "tool_calling": (3, 3)
}

# Generate evaluation data for the last 90 days
start_date = datetime.now() - timedelta(days=90)
dates = [
    start_date + timedelta(days=i)
    for i in range(90)
]

data = []
evaluation_id = 1

for date in dates:
    for category in categories:

        num_evaluations = np.random.randint(5, 16)

        for _ in range(num_evaluations):

            model = np.random.choice(model_versions)

            alpha, beta = distributions[category]

            score = np.random.beta(alpha, beta) * 100
            score += np.random.normal(0, 5)
            score = np.clip(score, 0, 100)

            data.append({
                "evaluation_id": evaluation_id,
                "category": category,
                "score": round(score, 2),
                "model_version": model,
                "date": date.strftime("%Y-%m-%d")
            })

            evaluation_id += 1

# Create and save raw dataset
df = pd.DataFrame(data)
df.to_csv("evaluation_data.csv", index=False)

# Clean and validate data
df = df.dropna(subset=["score", "category"])

assert len(df) >= 100
assert df["evaluation_id"].is_unique
assert pd.api.types.is_numeric_dtype(df["score"])
assert df["score"].between(0, 100).all()
assert df["category"].isin(categories).all()

pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")

# Export validated dataset for Tableau
df.to_csv(
    "evaluation_data_clean.csv",
    index=False,
    encoding="utf-8"
)

# Display validation results
print("\nDATA GENERATION SUCCESSFUL")
print("-" * 40)
print(f"Total evaluations: {len(df)}")
print(f"Categories: {df['category'].nunique()}")
print(f"Models: {df['model_version'].nunique()}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Missing values: {df.isna().sum().sum()}")
print(f"Duplicate IDs: {df['evaluation_id'].duplicated().sum()}")
print(f"Overall average score: {df['score'].mean():.2f}")

print("\nAverage scores by category:")
print(
    df.groupby("category")["score"]
    .mean()
    .sort_values(ascending=False)
    .round(2)
)

print("\nFirst five records:")
print(df.head().to_string(index=False))

print("\nAll validation checks passed.")
print("Created: evaluation_data.csv")
print("Created: evaluation_data_clean.csv")
