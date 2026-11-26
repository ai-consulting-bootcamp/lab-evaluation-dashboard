"""Steps 2-3: validate and clean the evaluation data for Tableau.

Checks (each prints PASS/FIX): numeric scores in 0-100, consistent category names, ISO dates,
no missing critical values, unique IDs, 100+ rows. Then adds stakeholder-friendly helper columns,
so the dashboard needs fewer calculated fields:
  category_label  "Instruction following" instead of "instruction_following"
  score_band      "0-9", "10-19", ... "90-100" (histogram bins with readable labels)
  result          "Pass" if score >= 70, else "Below target" (the business threshold used on the dashboard)
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
SRC, OUT = DATA / "evaluation_data.csv", DATA / "evaluation_data_clean.csv"
PASS_THRESHOLD = 70

df = pd.read_csv(SRC)
n0 = len(df)
print(f"Loaded {n0} rows, columns: {list(df.columns)}")

def check(ok, msg):
    print(("PASS  " if ok else "FIX   ") + msg)

# 1. numeric scores within 0-100
df["score"] = pd.to_numeric(df["score"], errors="coerce")
check(df["score"].between(0, 100).all(), "scores are numeric and within 0-100")

# 2. consistent categories (trim, lower-case, single spelling)
df["category"] = df["category"].astype(str).str.strip().str.lower().str.replace(" ", "_")
check(df["category"].nunique() == 5, f"5 consistent categories: {sorted(df['category'].unique())}")
df["model_version"] = df["model_version"].astype(str).str.strip()

# 3. ISO dates
df["date"] = pd.to_datetime(df["date"], errors="coerce")
check(df["date"].notna().all(), "all dates parse as YYYY-MM-DD")

# 4. missing critical values
before = len(df)
df = df.dropna(subset=["score", "category", "date"])
check(len(df) == before, f"no rows with missing score/category/date (removed {before - len(df)})")

# 5. unique ids, enough rows
check(df["evaluation_id"].is_unique, "evaluation_id is unique")
check(len(df) >= 100, f"{len(df)} rows (>= 100 needed for meaningful charts)")

# helper columns for non-technical labels
df["category_label"] = df["category"].str.replace("_", " ").str.capitalize()
df["score_band"] = pd.cut(df["score"], bins=list(range(0, 100, 10)) + [100.01], right=False,
                          labels=[f"{b}-{b + 9}" for b in range(0, 90, 10)] + ["90-100"]).astype(str)
df["result"] = (df["score"] >= PASS_THRESHOLD).map({True: "Pass", False: "Below target"})
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

cols = ["evaluation_id", "date", "model_version", "category", "category_label", "score", "score_band", "result"]
df[cols].to_csv(OUT, index=False, encoding="utf-8")
print(f"\nSaved {OUT.name}: {len(df)} rows, {len(cols)} columns, UTF-8, comma-delimited")
print(df[cols].head(3).to_string(index=False))
