---
presents: demo-autoresearch-loop.md
budget: 4 min
beats: 4
---

# Present: Run a Propose-Evaluate-Promote Cycle with Plugin Eval

A skill has no stack trace, so its only signal is its output, measured repeatedly. Four beats: the baseline decides the target, one variable per cycle, the rule makes the call, and the lesson is a mechanism that transfers.

------

## Beats

### Beat 1: The baseline picks the target (1 min)

**Open:** [Step 1: Meet the Skill, Then Capture Three Runs](demo-autoresearch-loop.md#step-1-meet-the-skill-then-capture-three-runs) · [`autoresearch-loop-solution/results/baseline/aggregate-result.json`](autoresearch-loop-solution/results/baseline/aggregate-result.json)
**Say:** `claude plugin eval` runs the case three times with the plugin and three times without, each in an empty workspace. Five of six measurements come back with no room in them, and that is knowable only after measuring.

```bash
claude plugin eval course-status --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir results/baseline
```

**Result:** every run read `evaluate.log`, and only two answers quoted it. The aggregate file holds the score.

```json
"durationSeconds": 75,
"costUsd": 0.531207,
"casesPassed": 0,
"overallScore": 0.9333333333333332,
"meanDelta": 0.9333333333333332
```

**Gotcha:** read `skill-fired` before the score; a run where the skill never loaded scored the model, so the score says nothing about your edit.

### Beat 2: A required artifact beats a required behaviour (1 min)

**Open:** [Step 2: Change One Sentence](demo-autoresearch-loop.md#step-2-change-one-sentence) · [`autoresearch-loop-solution/course-status/skills/course-status/SKILL.md`](autoresearch-loop-solution/course-status/skills/course-status/SKILL.md)
**Say:** The skill already said "never summarise from memory" and the trace showed the read every time. A claim in the answer is free; a line the model could only copy from the log is not.

```diff
+ Open the answer by quoting the `Evaluated` line of `course/evaluate.log` verbatim.
```

**Result:** one sentence, one line, in step 3. Nothing else in the file moved, which is what makes the next measurement attributable.

**Gotcha:** "add the sentence and tidy the wording" is two proposals. Ship it as one and the result explains nothing.

### Beat 3: The rule makes the decision (1 min)

**Open:** [Step 3: Re-measure, Then Write What Transfers](demo-autoresearch-loop.md#step-3-re-measure-then-write-what-transfers) · [`autoresearch-loop-solution/results/after/aggregate-result.json`](autoresearch-loop-solution/results/after/aggregate-result.json)
**Say:** Same command, same three runs, no peeking between them. Three conditions decide: the target passed in more runs, nothing else lost more than one run, no run errored.

**Result:** the prediction held and the rule says promote: `quotes-log` went from 2 of 3 to 3 of 3, and every other scored grader stayed where it was.

```json
"casesPassed": 1,
"overallScore": 1,
"meanDelta": 1,
"costUsd": 0.5233444
```

**Gotcha:** identical output across runs has no grader, because plugin eval scores each run on its own. That is the next cycle's question.

### Beat 4: The lesson is a mechanism (1 min)

**Open:** [`autoresearch-loop-solution/lessons.md`](autoresearch-loop-solution/lessons.md)
**Say:** "Proposal 1 improved quotes-log" is worth nothing next month. The reusable form names why it worked in terms that apply to a skill with nothing to do with dashboards.

**Result:** the entry that transfers.

```text
When a skill step must make the agent emit a specific quoted line, name the source file, the exact line and its position in the answer as an imperative in that step. A reason after the instruction does not reliably produce the line.
```

**Gotcha:** the lessons file is the compounding asset here. Everything else in the folder is one cycle's scaffolding.

## If the room asks

| Question | Answer |
|---|---|
| Why not run the repo's own `class-dashboard`? | An eval run loads only the plugin under test in an empty workspace, and on native Windows a run granted a shell is refused for want of a sandbox. The fixture holds what the evaluator wrote. |
| Why does the prompt name the skill? | This case measures the body. Naming the skill keeps the trigger out of the experiment; trigger accuracy is its own case. |
| What if the target improves but something else drops? | Revert. Trading one weakness for another leaves the skill with a different weakness, and the score should show that. |
