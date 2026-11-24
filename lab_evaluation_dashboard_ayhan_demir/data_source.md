# Data Source

**Option B: generated sample data.** I used the lab's generator script (seed 42) to create `evaluation_data.csv` and cleaned it into `evaluation_data_clean.csv` (4489 evaluations, 5 categories, 4 model versions, 2026-08-26 to 2026-11-23).
I chose Option B because my earlier lab outputs do not hold one file with categories, model versions and 90 days of dates together, which this dashboard needs for its filters.
The data is synthetic: scores follow fixed category patterns and the model version is assigned at random, so the dashboard shows the method, not real model performance.
