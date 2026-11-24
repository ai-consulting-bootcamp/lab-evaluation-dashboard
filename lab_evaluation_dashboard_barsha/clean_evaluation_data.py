import pandas as pd

df = pd.read_csv("evaluation_data.csv")

# 1. Check the structure
print("Rows:", len(df))
print("Types:\n", df.dtypes, "\n")

# 2. Fix types and remove rows with missing critical data
df["score"] = pd.to_numeric(df["score"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
before = len(df)
df = df.dropna(subset=["score", "category"])
df = df[(df.score >= 0) & (df.score <= 100)]
print(f"Removed {before - len(df)} rows with missing or out-of-range data")

# 3. Readable names for stakeholders
df["category"] = df["category"].str.replace("_", " ").str.title()
df["model_version"] = df["model_version"].map({
    "gpt-4": "GPT-4", "gpt-4-turbo": "GPT-4 Turbo",
    "gpt-3.5-turbo": "GPT-3.5 Turbo", "claude-3-opus": "Claude 3 Opus"})

# 4. Quick summary
print("\nCategories:", sorted(df.category.unique()))
print("Models:", sorted(df.model_version.unique()))
print("Date range:", df.date.min(), "to", df.date.max())
print("\nAverage score per category:\n", df.groupby("category")["score"].mean().round(1).sort_values())

df.to_csv("evaluation_data_clean.csv", index=False, encoding="utf-8")
print("\nSaved evaluation_data_clean.csv")