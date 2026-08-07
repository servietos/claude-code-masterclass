# Proposal

Target metric: `evaluator_evidence`, 0.00 at baseline.

Change (one variable only): add one sentence to step 3 of the `evaluate` sub-verb in
`.claude/skills/class-dashboard/SKILL.md`, requiring the answer to open by quoting the
evaluator's own stdout line verbatim. Nothing else in the skill changes.

Prediction: `evaluator_evidence` rises from 0.00 to 1.00. `sections_present` stays at
3.00, since it is already at ceiling. `identical_outputs` stays at 0, because the change
constrains one line of the answer and leaves the rest of the prose free.

Why this metric and not `sections_present`: the baseline already scores 3 of 3 there, so a
proposal aimed at it cannot show an improvement. `identical_outputs` at 0 of 3 pairs is
the larger defect, but closing it needs a full output template, which is more than one
variable.

Why it matters: all three baseline runs claimed a fresh evaluation in prose, and none
carried anything that could only come from running the script. The skill's own rule is
"never summarise from memory", and the baseline shows no way to check that from the answer.
