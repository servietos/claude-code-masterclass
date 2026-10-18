# Lessons

## A required quotation needs an imperative placement

**Pattern (2026-10-17):** A course-status step asked for the evaluator's line as a trailing justification ("so a reader can tell a fresh evaluation from a recalled one"), and the grader that checks for that line failed in one run of three. Rewriting the step as an imperative that names the source file and the answer's opening position made that grader pass in every run, so the edit was promoted. The proposal predicted every grader outcome; the surprise was in the baseline, where the same skill text had already failed the target in one run out of three, so the promotion rests on three runs and the edit's effect is not separated from that variance.

**Rule:** When a skill step must make the agent emit a specific quoted line, name the source file, the exact line and its position in the answer as an imperative in that step. A reason after the instruction does not reliably produce the line. Before promoting a change, check that the baseline target grader was stable across runs; a single failing run is inside the noise of a three-run sample.
