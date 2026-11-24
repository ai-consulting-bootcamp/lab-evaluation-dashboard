from pathlib import Path
import random
import pandas as pd

rng = random.Random(42)

# Assumed average scores for this simulation only.
category_means = {
    "Returns": (78, 84),
    "Delivery": (82, 86),
    "Refunds": (68, 77),
    "Cancellations": (75, 81),
    "Ambiguous requests": (58, 66),
}

versions = ["ShopCo_v1", "ShopCo_v2"]
records = []

for category, means in category_means.items():
    for version, mean_score in zip(versions, means):
        for _ in range(30):
            score = rng.gauss(mean_score, 14)
            score = round(max(0, min(100, score)), 2)

            records.append({
                "evaluation_id": f"SYN-{len(records) + 1:03d}",
                "category": category,
                "score": score,
                "model_version": version,
                "data_source": "synthetic",
            })

df = pd.DataFrame(records)

# Verify the generated dataset before saving.
assert len(df) == 300
assert df["evaluation_id"].is_unique
assert not df.isna().any().any()
assert df["score"].between(0, 100).all()
assert df.groupby(["category", "model_version"]).size().eq(30).all()

output_path = Path(__file__).resolve().parent / "evaluation_data_clean.csv"
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Saved: {output_path}")
print(f"Rows: {len(df)}")
print("Data source: synthetic — not real agent evaluations")
print("\nAverage simulated score by category and version:")
print(
    df.pivot_table(
        index="category",
        columns="model_version",
        values="score",
        aggfunc="mean",
    ).round(2)
)
print("\nValidation checks passed.")