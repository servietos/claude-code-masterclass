# Run a Feature Through the Four-Step Spec Kit Pipeline

A product owner's brief leaves gaps, and a coding agent fills them wherever you are not looking. Take a meeting cost calculator from that brief to tested code with GitHub Spec Kit in Claude Code, reading each artifact before the next phase starts.

What you practice here: holding each generated artifact against its source at a checkpoint before the next phase reads it.

Duration: about 25 minutes.

------

Run [setup-speckit.ps1](setup-speckit.ps1) on Windows or [setup-speckit.sh](setup-speckit.sh) elsewhere, then start `claude` in `~/spec-runs/meeting-cost`, the copy of [meeting-cost/](meeting-cost/) it creates; the finished project is in [meeting-cost-solution/](meeting-cost-solution/readme.md).

## Step 1: Specify and Close the Gaps

Run `/speckit-constitution` with the six principles from [constitution.md](meeting-cost/constitution.md) and count them, because the template has five principle slots. Then run `/speckit-specify` with the Request, User stories, Acceptance criteria, Constraints and Edge cases sections of [requirements.md](meeting-cost/requirements.md).

The recorded run raised three questions and listed an assumption of its own that gives attendees a label the brief never asked for. Answer the questions and remove the label in the same session:

```text
Q1: B, out of scope; the team lead multiplies the printed total.
Q2: Custom: round the total half up to two decimal places; breakdown values stay unrounded; "the breakdown sums to the total" means it sums to the total before rounding.
Q3: A, amounts are currency-agnostic decimals with no symbol.
One more correction: attendees are a list of hourly rates and nothing more. Remove the optional label from the Attendee entity and the Assumptions; identify an attendee by their position in the list. Write all of this into spec.md under a Resolved Gaps heading and update FR-004, FR-007 and FR-008 to match.
```

A `Resolved Gaps` section lands in `spec.md`, and the markers are replaced by your rules:

```diff
-- **FR-007**: Monetary amounts MUST be rounded as follows: [NEEDS CLARIFICATION: rounding rule not specified. To what precision, with which rounding mode, and is rounding applied per attendee or to the total?]
+- **FR-007**: The total MUST be rounded half up to two decimal places. Breakdown values MUST NOT be rounded.
-- **Attendee**: a participant with an hourly rate and an optional label used to identify them in the breakdown and in error messages.
+- **Attendee**: an hourly rate in the meeting's list of rates, identified by its position in that list.
```

The brief's two unstated details are decided here, in writing, by you.

## Step 2: Plan Against the Constitution

The plan adds the stack and the design, and it must verify itself against every principle. `/speckit-analyze` then reads spec, plan and tasks together without editing anything, which is the last cheap moment to find a conflict.

```text
/speckit-plan Use Python 3.11 with pytest, standard library only. A flat package meeting_cost with two modules, the calculation logic and a CLI wrapper using argparse, plus a __main__.py so it runs as python -m meeting_cost <minutes> <rate> [<rate> ...].
```

The plan's summary flags that your usage line requires at least one rate while FR-011 allows zero attendees; tell Claude the spec wins. Then run `/speckit-tasks` and `/speckit-analyze`, which found a constitution conflict every earlier checkpoint had missed:

```text
| C1 | Constitution III / FR-009 | CRITICAL | plan.md:13, research.md R5, tasks.md T018 | argparse only accepts a plain negative number like `-5` or `-.5` as a positional. Inputs such as `-1e3`, `-abc` or `-inf` fail with `unrecognized arguments: ...`, which doesn't name the field. Reproduced. |
```

Approve the remediation for C1 in the same session, and the plan, contract and task list change before any code exists.

## Step 3: Implement, Verify and Converge

Run `/speckit-implement`, then `/speckit-converge`. The recorded converge appended a crash on `python -m meeting_cost 60 1e30`, then found the same crash at `1e999999`, because the spec's Assumptions allow any size. Change the requirement:

```text
In specs/001-meeting-cost-calculator/spec.md add a requirement FR-014 (or the next free FR number): a duration above 1440 minutes or an hourly rate above 100000 is invalid input and is rejected with a message naming the field, like any other invalid value. Remove any assumption that says duration or rate has no upper limit, and add the edge case and a Resolved Gaps line for it. Then delete every unfinished task in tasks.md that the new requirement replaces, such as a task about very large durations or rates, and name the tasks you deleted. Change nothing else.
```

Then run `/speckit-converge`, `/speckit-implement` and `/speckit-converge` again; the last converge leaves `tasks.md` unchanged:

```text
No gaps found. `tasks.md` is unchanged.

✅ **Converged: the code does everything the spec, plan and tasks ask for.**
```

Each fix invited the next until the requirement changed; `python -m pytest` then reports `30 passed`.
