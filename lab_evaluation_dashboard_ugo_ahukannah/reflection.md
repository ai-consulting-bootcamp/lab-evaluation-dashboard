# Reflection

**LAB | Evaluation Dashboard** &mdash; optional reflection
**Author:** Nnanyelugo Ahukannah

**Applying the communication layer.** The analysis this dashboard sits on has five
evaluators, a judge-versus-checker agreement audit, and a finding about a judge
contradicting its own reasoning. None of that is on the dashboard. What survived
is the three questions a stakeholder actually asks &mdash; is it good enough, where
does it fail, and can we trust the measurement &mdash; and every chart is titled as
the question it answers rather than the field it plots. The hardest discipline was
naming: `citation_validity` became *Points to the right source*, and `terse`
became *Standard model, reduced instructions*, because a label a reader has to
decode is a label that stops them reading. I kept the raw keys in parallel columns
in the CSV so the mapping stays auditable, which is the compromise between plain
language and a number nobody can trace.

**What I included versus excluded, and what I would change.** Excluded: p-values,
sample sizes, model version strings, prompt text, anything about how the
evaluators work. Included: one number per question, filters so people can check
their own segment rather than emailing me for a cut, and a sentence of context per
dashboard stating the conclusion. The most useful decision was building a second
dashboard for reviewer reliability instead of putting an agreement figure on the
main one &mdash; "can we trust this?" is a different question from "how good is
it?", and mixing them invites a reader to average two things that should not be
averaged. What I would do differently: the score distribution is honest but thin
at this sample size, and I would rather show a count of examples per band with the
band definitions written out than an axis a reader has to interpret. I would also
add a plain "last refreshed" stamp; the date field exists in the data and is not
yet surfaced, and a dashboard with no visible age is one people quietly stop
trusting.
