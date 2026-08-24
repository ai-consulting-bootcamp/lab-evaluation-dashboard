# Step 2: Clean and Format Data

Started with 4489 rows from `evaluation_data.csv`.

- Score not numeric: 0 row(s) found and dropped.
- Categories standardized (trimmed, lowercased). Unique values: ['code', 'instruction_following', 'knowledge', 'reasoning', 'tool_calling']
- Dates not in YYYY-MM-DD: 0 row(s) found.
- Rows dropped for missing critical data (score/category/date): 0
- Duplicate evaluation_id rows removed: 0

Final row count: 4489 (started with 4489).

## Sanity check
- Score range: 0.0 to 100.0
- Categories: ['code', 'instruction_following', 'knowledge', 'reasoning', 'tool_calling']
- Model versions: ['claude-3-opus', 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']
- Date range: 2026-05-26 to 2026-08-23
- Missing values remaining: 0
