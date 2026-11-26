"""Steps 2-3: check and prepare evaluation_data.csv for Power BI -> evaluation_data_clean.csv.
Adds two columns stakeholders can read without statistics: a plain-English category name and a score band."""
import pandas as pd

df = pd.read_csv('evaluation_data.csv')
checks = {
    "rows": len(df),
    "score_is_numeric": pd.api.types.is_numeric_dtype(df['score']),
    "score_in_0_100": bool(df['score'].between(0, 100).all()),
    "missing_score_or_category": int(df[['score', 'category']].isna().any(axis=1).sum()),
    "categories": sorted(df['category'].unique()),
    "models": sorted(df['model_version'].unique()),
    "dates_valid": bool(pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce').notna().all()),
}
for k, v in checks.items():
    print(f"{k}: {v}")

df = df.dropna(subset=['score', 'category'])
labels = {'reasoning': 'Reasoning', 'knowledge': 'Knowledge', 'code': 'Code',
          'instruction_following': 'Following instructions', 'tool_calling': 'Using tools'}
df['category_name'] = df['category'].map(labels)
bands = [(0, 40, '1 Poor (0-40)'), (40, 60, '2 Fair (40-60)'), (60, 80, '3 Good (60-80)'), (80, 100.01, '4 Excellent (80-100)')]
df['score_band'] = pd.cut(df['score'], bins=[b[0] for b in bands] + [bands[-1][1]], labels=[b[2] for b in bands], right=False)
df.to_csv('evaluation_data_clean.csv', index=False, encoding='utf-8')
print("Saved evaluation_data_clean.csv with", len(df), "rows and columns:", list(df.columns))
print(df.groupby('category_name')['score'].mean().round(1).sort_values())

# Power BI on a Spanish-locale Windows read "17.18" as 1718 (the dot is a thousands separator there).
# This copy uses ";" as separator and "," as decimal mark, and is the file the dashboard imports.
df.to_csv('evaluation_data_clean_powerbi_es.csv', index=False, sep=';', decimal=',', encoding='utf-8')
print("Saved evaluation_data_clean_powerbi_es.csv (Spanish-locale copy for Power BI)")
