"""Step 2: Clean and Format Data.

Reads evaluation_data.csv, checks it against the requirements in
instructions.md (numeric scores, consistent categories, consistent dates,
no missing critical values), fixes what it can, and saves the result as
evaluation_data_clean.csv. Also writes cleaning_check.md with the results,
so the check is documented, not just printed and lost.
"""

import pandas as pd

INPUT_FILE = "evaluation_data.csv"
OUTPUT_FILE = "evaluation_data_clean.csv"
REPORT_FILE = "cleaning_check.md"


def clean_and_check(df: pd.DataFrame):
    report_lines = ["# Step 2: Clean and Format Data\n"]
    report_lines.append(f"Started with {len(df)} rows from `{INPUT_FILE}`.\n")

    # 1. Scores must be numeric
    before = len(df)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    bad_scores = df["score"].isna().sum()
    report_lines.append(f"- Score not numeric: {bad_scores} row(s) found and dropped.")

    # 2. Categories: strip whitespace, lowercase, so small typos don't split a category in two
    df["category"] = df["category"].astype(str).str.strip().str.lower()
    report_lines.append(f"- Categories standardized (trimmed, lowercased). Unique values: {sorted(df['category'].unique())}")

    # 3. Dates must be valid and in YYYY-MM-DD format
    parsed_dates = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    bad_dates = parsed_dates.isna().sum()
    df["date"] = parsed_dates.dt.strftime("%Y-%m-%d")
    report_lines.append(f"- Dates not in YYYY-MM-DD: {bad_dates} row(s) found.")

    # 4. Drop rows missing any critical field
    critical_cols = ["score", "category", "date"]
    missing_before = len(df)
    df = df.dropna(subset=critical_cols)
    dropped = missing_before - len(df)
    report_lines.append(f"- Rows dropped for missing critical data (score/category/date): {dropped}")

    # 5. Drop duplicate evaluation_id, if any
    dup_count = df["evaluation_id"].duplicated().sum()
    df = df.drop_duplicates(subset="evaluation_id")
    report_lines.append(f"- Duplicate evaluation_id rows removed: {dup_count}")

    after = len(df)
    report_lines.append(f"\nFinal row count: {after} (started with {before}).\n")

    # Sanity check summary
    report_lines.append("## Sanity check")
    report_lines.append(f"- Score range: {df['score'].min()} to {df['score'].max()}")
    report_lines.append(f"- Categories: {sorted(df['category'].unique())}")
    report_lines.append(f"- Model versions: {sorted(df['model_version'].unique())}")
    report_lines.append(f"- Date range: {df['date'].min()} to {df['date'].max()}")
    report_lines.append(f"- Missing values remaining: {int(df.isnull().sum().sum())}")

    return df, "\n".join(report_lines)


def main():
    df = pd.read_csv(INPUT_FILE)
    clean_df, report = clean_and_check(df)

    clean_df.to_csv(OUTPUT_FILE, index=False)
    with open(REPORT_FILE, "w") as f:
        f.write(report + "\n")

    print(report)
    print(f"\nSaved cleaned data to {OUTPUT_FILE}")
    print(f"Saved report to {REPORT_FILE}")


if __name__ == "__main__":
    main()
