---
presents: demo-autoresearch-loop.md
budget: 4 min
beats: 4
---

# Present: Run a Propose-Evaluate-Promote Cycle on a Live Skill

A skill has no stack trace, so its only signal is its output, measured repeatedly. Four beats: the baseline decides the target, one variable per cycle, the rule decides rather than the author, and the lesson is a mechanism rather than an outcome.

------

## Beats

### Beat 1: The baseline picks the target, not the author (1 min)

**Open:** [Step 1: Meet the Skill, Then Capture Three Runs](demo-autoresearch-loop.md#step-1-meet-the-skill-then-capture-three-runs) · [`autoresearch-loop-solution/baseline.json`](autoresearch-loop-solution/baseline.json)
**Say:** Three runs of one prompt, captured before anyone reads the skill. Two of the four metrics come back with no room in them, and that is knowable only after measuring.

**Result:** the numbers rule out two targets immediately.

```text
baseline: 3 runs
  identical_outputs  0 of 3 pairs
  sections_present   3 of 3
  evaluator_evidence 0
  abort_rate         0
```

**Gotcha:** a proposal aimed at `sections_present` here can only stay flat or regress. Picking the target before the baseline is how a cycle gets wasted.

### Beat 2: A required artifact beats a required behaviour (1 min)

**Open:** [Step 3: Change One Sentence](demo-autoresearch-loop.md#step-3-change-one-sentence) · [`.claude/skills/class-dashboard/SKILL.md`](../../../.claude/skills/class-dashboard/SKILL.md)
**Say:** The skill already said "never summarise from memory" and every baseline run complied with it in prose while proving nothing. A claim is free; a value the model could only have obtained by running the script is not.

```diff
+ Open the report by quoting the evaluator's own stdout line verbatim (`Evaluated 13 modules -> ...`), so a reader can tell a fresh evaluation from a recalled one.
```

**Result:** one sentence, one line, on one sub-verb. Nothing else in the file moved, which is what makes the next measurement attributable.

**Gotcha:** "add the sentence and tidy the wording" is two proposals. Ship it as one and the result explains nothing.

### Beat 3: The rule decides, the author does not (1 min)

**Open:** [Step 4: Re-measure, Then Write What Transfers](demo-autoresearch-loop.md#step-4-re-measure-then-write-what-transfers) · [`autoresearch-loop-solution/after.json`](autoresearch-loop-solution/after.json)
**Say:** Same prompt, same three runs, no peeking between them. Three conditions decide: target improved, nothing else regressed by more than a unit, aborts still zero.

**Result:** the prediction held on all four metrics and the harness printed the verdict.

```text
target metric      evaluatorEvidence: 0 -> 1
regressed          none
DECISION           PROMOTE
```

**Gotcha:** `identical_outputs` stayed at 0 of 3 pairs, exactly as predicted. That is the next cycle's proposal, not this cycle's failure, and saying so out loud is the point.

### Beat 4: The lesson is a mechanism, not an outcome (1 min)

**Open:** [`autoresearch-loop-solution/lessons.md`](autoresearch-loop-solution/lessons.md)
**Say:** "Proposal 1 improved evaluator_evidence" is worth nothing next month. The reusable form names why it worked in terms that apply to a skill with nothing to do with dashboards.

**Result:** the entry that transfers.

```text
An instruction that asks the model to report that it did something scores nothing,
because a claim is free. An instruction that asks it to carry a value it could only
have obtained by doing the thing is checkable from the output alone.
```

**Gotcha:** the lessons file is the compounding asset here. Everything else in the folder is one cycle's scaffolding.

## If the room asks

| Question | Answer |
|---|---|
| Why three runs and not one? | One run measures a sample, not a distribution. Three is the floor; five is better for a skill going into production. |
| Why not fix `identical_outputs`, the worse number? | It needs a full output template, which is more than one variable. One line cannot constrain a whole document, and the measurement confirmed it. |
| What if the target improves but something else drops? | Revert. A skill that traded one weakness for another is a different skill, not a better one. |
| Does the promoted change stay in the repo? | Yes, that is what promotion means. Cleanup removes the experiment artifacts, not the winning edit. |
