# Reflection

**How I applied the communication layer.**
- **Titles state conclusions.** For example, *"Only 3 in 10 evaluations reach the target score of 70"* or *"Reasoning is the weakest category"*, rather than chart names like "Score histogram".
- **Readers move from headline to evidence:** KPI cards first, then the category ranking, then the distribution, then detail.
- **One business threshold** (a score of 70 = pass) turns a statistical distribution into the question a manager asks: "how often is it good enough?".
- **Plain-language labels** replace technical ones: "Instruction following", not `instruction_following`; "the middle half of the scores", not "IQR".
- **No statistical methods appear:** no p-values, confidence intervals, standard deviations or test names. The box plot carries a one-sentence explanation, and every filter applies to the whole dashboard, so two charts never disagree.

**What I included vs excluded.**
- **Included:** what stakeholders decide on: overall performance, where it fails (by category), whether the model choice matters, and filters to explore by model, category and period.
- **Excluded,** and kept in the analysis notebooks and scripts: data cleaning, distribution parameters, judge methodology, per-run raw data and significance testing.
- **The judge-agreement dashboard** shows reliability in one sentence ("runs within 25 points agree"), instead of agreement statistics such as Cohen's kappa.

**What I would do differently.**
- **Watch for artefacts in synthetic data.** The near-identical model scores come from the generator assigning models at random. With real data I would check that before presenting "model doesn't matter" as a finding.
- **Use my own evaluation data for the main dashboard,** with more cases and dates.
- **Test the dashboard** with one non-technical person before calling it finished.
