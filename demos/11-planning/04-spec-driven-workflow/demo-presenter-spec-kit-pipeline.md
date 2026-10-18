---
presents: demo-spec-kit-pipeline.md
budget: 4 min
beats: 4
---

# Present: Run a Feature Through the Four-Step Spec Kit Pipeline

The room leaves knowing that the checkpoints are the method: each one caught something the next phase would have built on. Four beats: the invented attendee label, the contract that contradicted the spec, the CRITICAL finding before any code, and the converge loop that only a spec change could end.

------

**Shell:** setup ships twice, [`setup-speckit.ps1`](setup-speckit.ps1) on Windows and [`setup-speckit.sh`](setup-speckit.sh) elsewhere; both copy the starter to `~/spec-runs/meeting-cost` and run `specify init . --integration claude`. The beats quote only prompts typed inside the session, identical on both shells.

## Beats

### Beat 1: the decided item hides under Assumptions (1 min)

**Open:** [`meeting-cost/requirements.md`](meeting-cost/requirements.md) · [Step 1: Specify and Close the Gaps](demo-spec-kit-pipeline.md#step-1-specify-and-close-the-gaps)
**Say:** Claude raised both deliberate gaps as questions. What it decided without asking sat in the Assumptions section: a label per attendee nobody requested.

```text
Q1: B, out of scope; the team lead multiplies the printed total.
Q2: Custom: round the total half up to two decimal places; breakdown values stay unrounded; "the breakdown sums to the total" means it sums to the total before rounding.
Q3: A, amounts are currency-agnostic decimals with no symbol.
One more correction: attendees are a list of hourly rates and nothing more. Remove the optional label from the Attendee entity and the Assumptions; identify an attendee by their position in the list. Write all of this into spec.md under a Resolved Gaps heading and update FR-004, FR-007 and FR-008 to match.
```

**Result:** the answers landed as written rules in [`spec.md`](meeting-cost-solution/specs/001-meeting-cost-calculator/spec.md)

```markdown
- **Annual cost (Q1)**: Out of scope. The team lead multiplies the printed total by occurrences per year (FR-019).
- **Rounding (Q2)**: The total is rounded half up to two decimal places. The breakdown amounts stay unrounded. "The breakdown sums to the total" means the breakdown sums to the total before rounding (FR-006, FR-007).
- **Currency (Q3)**: Amounts are currency-agnostic decimals with no symbol (FR-008).
- **Attendee identity**: Attendees are a list of hourly rates and nothing more. No name or label is captured. An attendee is identified by its position in the list, such as first or second.
```

**Gotcha:** read Assumptions before the requirements; a gap closed there is still a decision you did not make.

### Beat 2: the contract contradicted the spec, and Claude said so (1 min)

**Open:** [`contracts/cli.md`](meeting-cost-solution/specs/001-meeting-cost-calculator/contracts/cli.md) · [Step 2: Plan Against the Constitution](demo-spec-kit-pipeline.md#step-2-plan-against-the-constitution)
**Say:** Tests are written against the contract. A contract that disagrees with the spec ships code that disagrees with it, behind a green suite.

```text
/speckit-plan Use Python 3.11 with pytest, standard library only. A flat package meeting_cost with two modules, the calculation logic and a CLI wrapper using argparse, plus a __main__.py so it runs as python -m meeting_cost <minutes> <rate> [<rate> ...].
```

**Result:** the `rate` row of the generated [`cli.md`](meeting-cost-solution/specs/001-meeting-cost-calculator/contracts/cli.md) contract

```markdown
| `rate` | One hourly rate per attendee, in the order the breakdown should list them. Zero or more. |
```

**Gotcha:** the conflict came from the usage line in the plan prompt itself; the spec still wins.

### Beat 3: analyze found a CRITICAL conflict before a line of code (1 min)

**Open:** [Step 2: Plan Against the Constitution](demo-spec-kit-pipeline.md#step-2-plan-against-the-constitution) · [`meeting_cost/cli.py`](meeting-cost-solution/meeting_cost/cli.py)
**Say:** `/speckit-analyze` writes nothing; it reads three documents against the constitution. It reproduced that argparse swallows `-abc` before the field-naming error can fire.

```text
Apply the remediation for C1 and I1 only. Edit plan.md, research.md, contracts/cli.md and tasks.md so every argument after the program name reaches calculate_cost and a value such as -abc or -1e3 fails with the named field, add a CLI test task for those two values, and fix the T021 ordering. Leave the other findings as they are.
```

**Result:** the `rate` argument in [`cli.py`](meeting-cost-solution/meeting_cost/cli.py)

```python
    parser.add_argument("rates", nargs="*", help="one hourly rate per attendee")
```

**Gotcha:** the price is visible in the usage line: there is no `-h` any more, because every argument is input.

### Beat 4: converge chased inputs until the requirement changed (1 min)

**Open:** [`tasks.md`](meeting-cost-solution/specs/001-meeting-cost-calculator/tasks.md) · [Step 3: Implement, Verify and Converge](demo-spec-kit-pipeline.md#step-3-implement-verify-and-converge)
**Say:** Converge reads the spec literally. "No upper limit" meant `1e30`, then `1e999999`, and each fix invited the next.

```text
In specs/001-meeting-cost-calculator/spec.md add a requirement FR-014 (or the next free FR number): a duration above 1440 minutes or an hourly rate above 100000 is invalid input and is rejected with a message naming the field, like any other invalid value. Remove any assumption that says duration or rate has no upper limit, and add the edge case and a Resolved Gaps line for it. Then delete every unfinished task in tasks.md that the new requirement replaces, such as a task about very large durations or rates, and name the tasks you deleted. Change nothing else.
```

**Result:** FR-014 became two constants in [`calculation.py`](meeting-cost-solution/meeting_cost/calculation.py), and the next converge reported `✅ **Converged: the code does everything the spec, plan and tasks ask for.**`

```python
MAX_DURATION_MINUTES = Decimal("1440")
MAX_HOURLY_RATE = Decimal("100000")
```

**Gotcha:** `tasks.md` keeps an empty `## Phase 8: Convergence` heading, because converge only appends and the deleted task left it behind.

## If the room asks

| Question | Answer |
|---|---|
| Are these slash commands? | They are skills under `.claude/skills/` with `user-invocable: true`, so they appear in the slash menu; `disable-model-invocation: false` also lets Claude load one on its own. |
| Why does the run folder live outside the repository? | Claude Code loads `CLAUDE.md` files from parent folders, so a run inside this checkout would carry the course repository's own instructions, and the starter stays pristine. |
| Is the overhead worth it? | The recorded run took 17 prompts for a 69-line module. It pays off when someone will hold you to the acceptance criteria, and a one-line fix is better served by a direct prompt. |

## Runs live instead

A learner running it types every prompt and reads every artifact at its checkpoint, and their Claude will word things differently: [Run a Feature Through the Four-Step Spec Kit Pipeline](demo-spec-kit-pipeline.md).
