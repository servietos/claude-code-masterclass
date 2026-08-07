# Lessons

## Cycle 1: evidence beats assertion in a skill's output contract

Proposal: require the `evaluate` sub-verb's answer to open by quoting the evaluator's own
stdout line verbatim. Target metric `evaluator_evidence`, 0.00 to 1.00 over three runs.
Promoted.

What generalises: an instruction that asks the model to report that it did something scores
nothing, because a claim is free. An instruction that asks it to carry a value it could only
have obtained by doing the thing is checkable from the output alone. The skill already said
"never summarise from memory", and no baseline run violated anything observable, because
there was no observable to violate. Prefer a required artifact over a required behaviour
when writing a skill's output contract.

The metric that moved was picked after the baseline, not before. `sections_present` sat at
its 3.00 ceiling in every baseline run, so a proposal aimed at it could only stay flat or
regress. Read the baseline before writing the proposal, or a cycle gets spent on a metric
with no room in it.

## Cycle 1 side finding: identical_outputs needs a template, not a rule

`identical_outputs` stayed at 0 of 3 pairs across both measurements, exactly as predicted.
All six runs agreed on every number (13 modules, 43 of 52 components, 83%) and disagreed on
prose, column count and ordering. Constraining one line does not constrain a document.

Next proposal to try: a fixed output template (ordered headings plus a fixed column list)
targeting `identical_outputs`, with `evaluator_evidence` watched for regression. Do not
combine it with any wording change, or attribution is lost.
