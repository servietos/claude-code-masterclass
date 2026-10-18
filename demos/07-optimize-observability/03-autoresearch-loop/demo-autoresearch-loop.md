# Run a Propose-Evaluate-Promote Cycle with Plugin Eval

A skill that answers slightly differently every time gets edited on a hunch, and nobody can tell afterwards whether the edit helped. You measure the starter's `course-status` skill with `claude plugin eval` over three runs, change one sentence in it, re-measure under identical conditions, and let a rule decide.

------

Work in `autoresearch-loop/` (nothing to install; the subject is the plugin in `course-status/`); the finished result is beside it in [`autoresearch-loop-solution/`](autoresearch-loop-solution).

## Step 1: Meet the Skill, Then Capture Three Runs

You cannot trust a score whose graders you have not read. Read the case and its graders first, then capture three runs of the identical prompt without reading them, because three runs is the smallest thing that distinguishes a real change from a lucky sample.

```text
Read course-status/skills/course-status/SKILL.md and every file under
course-status/evals/class-status/. Tell me what the case asks, what each grader checks,
and which grader is only an indicator.
Then run the baseline from this folder, and do not read the answers in between:
claude plugin eval course-status --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir results/baseline
Then read results/baseline/aggregate-result.json and tell me, for each grader in the
with-arm, how many of the three runs passed it, and how many runs ended with an error.
```

Six graders come back, with `skill-fired` named as the indicator plugin eval never scores, and the aggregate file reports a mean Δ of +0.93 and a run cost of $0.53.

Every run read `evaluate.log`, which the trace proves, and only two answers carried the evaluator's own line: `quotes-log` at 2 of 3 is the one scored grader with room.

## Step 2: Change One Sentence

The proposal names one target, one variable and a prediction. The skill already says "never summarise from memory", so the edit adds an artifact only a real read can produce.

```text
Write proposal.md with three fields and nothing else: Target grader, Change (one
variable, naming the file and step), Prediction (what the target does and what every
other grader does). Then say why you did not target the others.
Apply the change from proposal.md to course-status/skills/course-status/SKILL.md. Edit
only step 3, change nothing else, and show me the diff.
The answer must open by quoting the evaluator's own line from course/evaluate.log
verbatim, so a reader can tell a fresh evaluation from a recalled one.
```

One sentence, one line, and the [`proposal.md`](autoresearch-loop-solution/proposal.md) prediction that nothing else moves is what makes Step 3 falsifiable:

```diff
-3. Give the overall completion percentage and name every component still `planned` or `doing`. Never summarise from memory.
+3. Give the overall completion percentage and name every component still `planned` or `doing`. Never summarise from memory. Open the answer by quoting the `Evaluated` line of `course/evaluate.log` verbatim.
```

## Step 3: Re-measure, Then Write What Transfers

Identical conditions means the same command and the same run count, with no reading until all three are captured. The decision is then arithmetic, and the lesson is written against the prediction.

```text
Run the same command again, writing to results/after:
claude plugin eval course-status --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir results/after
Compare results/baseline/aggregate-result.json with results/after/aggregate-result.json,
grader by grader, in the with-arm. Check skill-fired first. Then apply the rule: PROMOTE
only if the target grader passed in more runs, no other scored grader lost more than one
run, and no run ended with an error; otherwise REVERT.
Then append a cycle entry to lessons.md: the decision, the mechanism that generalises
stated so it applies to a skill with nothing to do with dashboards, and the one thing
the measurement showed that the proposal did not predict. No restating the numbers.
```

The prediction held and the rule decided, DECISION: PROMOTE:

| Grader | Baseline | After |
|---|---|---|
| `quotes-log` (target) | 2 of 3 | 3 of 3 |
| every other scored grader | 3 of 3 | 3 of 3 |
| `skill-fired` (indicator) | 3 of 3 | 3 of 3 |
| runs with an error | 0 | 0 |
