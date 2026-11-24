# Reflection

## Which communication-layer principles did I apply?
- **Lead with the "so what".** The top chart is the sorted average-score bar, because it answers the main question first: which task types are strong and which are weak. A short text box states the key takeaway in plain language (Reasoning is the weakest area at ~41; Instruction Following and Knowledge are strengths).
- **Give context for every number.** The text explains the scale (0–100, 100 = perfect), the number of evaluations (4,489) and the date range. An overall-average reference line shows at a glance which categories are above or below average.
- **Simple, labelled visuals.** Each chart has a descriptive title (what it shows + how to read it), readable axis titles instead of raw field names, value labels with one decimal, and categories sorted from lowest to highest.
- **Purposeful colour.** A single blue gradient encodes average score (lighter = weaker). No decorative colours.
- **Let the audience explore.** Filters for model version, category and date apply to all three charts, so a stakeholder can answer their own follow-up questions.

## What did I include and what did I leave out?
**Included:** score distribution (histogram), spread per category (box plot), average per category (sorted bar with reference line), the key takeaway, and filters.

**Left out on purpose:** p-values, confidence intervals, statistical test results, raw data tables, and the individual evaluation IDs. A business audience needs to know *what* is happening and *where to act*, not the statistical machinery. I also kept the number of charts to three so the dashboard can be understood in under a minute.

## How is this dashboard different from an analysis notebook?
An analysis notebook is for the analyst. It shows the full process: data cleaning, exploratory plots, statistical tests, assumptions, and dead ends, and it is read top to bottom. This dashboard is the communication layer for decision-makers. It only shows the conclusions that matter, in a format that is interactive and can be read at a glance, without any code or statistical jargon. The notebook answers "is this result real and how did we get it?"; the dashboard answers "what does it mean and what should we do?".