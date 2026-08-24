# Data Source

**LAB | Evaluation Dashboard** &mdash; Step 1
**Author:** Nnanyelugo Ahukannah

This dashboard uses **Option A: real results from my own earlier evaluation work**, not the
generated sample data.

The scores come from two evaluation runs I built and ran in previous labs. The main dataset is a
LangSmith experiment comparing three configurations of a grounded question-answering system over
a 22-question consumer-credit compliance set, scored by five evaluators &mdash; giving 396 rows
across four question categories, three difficulty levels and three model configurations. The
judge-agreement dataset pairs an LLM judge's verdict against a deterministic rule checker on the
same 76 graded items, drawn from that experiment plus a second run in which an LLM judge scored
automated compliance letters.

`prepare_dashboard_data.py` reshapes both into the tidy CSVs the BI tool reads. It renames every
metric and configuration into plain English, scales scores to 0&ndash;100, and adds one
**Overall quality score** row per example &mdash; the mean of its five metrics &mdash; because
each raw metric is 0 or 1 and a histogram of a binary column is two bars and tells a stakeholder
nothing. The raw keys are kept in parallel columns so the mapping stays auditable.

All underlying data is fictional: the client, the corpus and the letters were authored for a
teaching exercise, and nothing here is real customer information.
