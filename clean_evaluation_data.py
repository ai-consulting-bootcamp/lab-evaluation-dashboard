"""Steps 2-3: validate the raw evaluation CSV and write the file Tableau connects to.

Checks: numeric scores in 0-100, a fixed category vocabulary, ISO dates, no missing
score/category, unique IDs. Rows that fail are dropped and counted. Adds
`category_label` (business-friendly names for the dashboard). Score bands are left
to a Tableau calculated field, so the cleaned file stays one row per evaluation.

Output: evaluation_data_clean.csv
"""
import pandas as pd

LABELS = {
    'reasoning': 'Reasoning',
    'knowledge': 'Knowledge',
    'code': 'Code',
    'instruction_following': 'Instruction Following',
    'tool_calling': 'Tool Calling',
}

df = pd.read_csv('evaluation_data.csv')
n_raw = len(df)

df['category'] = df['category'].str.strip().str.lower()
df['model_version'] = df['model_version'].str.strip()
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

checks = {
    'missing score or category': df['score'].isna() | df['category'].isna(),
    'score outside 0-100': ~df['score'].between(0, 100),
    'unknown category': ~df['category'].isin(LABELS),
    'unparseable date': df['date'].isna(),
    'duplicate evaluation_id': df['evaluation_id'].duplicated(),
}
bad = pd.Series(False, index=df.index)
for name, mask in checks.items():
    print(f"{name:28s} {int(mask.sum())}")
    bad |= mask
df = df[~bad].copy()

df['category_label'] = df['category'].map(LABELS)
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
df = df[['evaluation_id', 'category', 'category_label', 'score', 'model_version', 'date']]
df.to_csv('evaluation_data_clean.csv', index=False, encoding='utf-8')

print(f"\nrows: {n_raw} raw -> {len(df)} clean ({n_raw - len(df)} dropped)")
print(f"dtypes: {dict(df.dtypes.astype(str))}")
print(f"categories: {sorted(df['category'].unique())}")
print(f"models: {sorted(df['model_version'].unique())}")
print(f"dates: {df['date'].min()} to {df['date'].max()}")
print("\nmean score by category x model (sanity check for the dashboard):")
print(df.pivot_table(index='category_label', columns='model_version',
                     values='score', aggfunc='mean').round(1))
