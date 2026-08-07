# Baseline Comparison

Status: NOT MEASURED in this run.

The protocol in Step 3 of the demo guide requires two fresh interactive Claude Code sessions and the
token totals reported by `/cost`. Neither is reachable from a non-interactive run: `/cost` is a client
side slash command whose output is printed to the terminal and never written to a file, and a session
cannot start a second fresh session of itself. The guide's own instruction, "Report measured numbers
only. Do not estimate any figure you did not observe.", therefore leaves this table empty rather than
filled with plausible looking figures.

| Metric | Without skill (Run A) | With skill (Run B) |
|---|---|---|
| Defects found of 3 planted | not measured | not measured |
| User messages to reach a verdict | not measured | not measured |
| Critical / Improvements split present | not measured | not measured |
| Token total from `/cost` | not measured | not measured |

## How to fill this in

1. Open a terminal, run `claude`, and prompt: "Review my changes and flag anything risky before I push."
   Record the answer, then run `/cost` and copy the totals by hand.
2. Exit, start a second session, prompt "Review my changes.", and repeat the `/cost` capture.
3. To make Run A a genuine no-skill run, the skill has to be unreachable, not merely unmentioned.
   Start that session with `claude --disallowedTools Skill`, which removes the Skill tool so nothing
   on disk has to move. Asking the model not to use a loaded skill is not a control condition.

Until those two captures exist, no distribution claim in `dist/README.md` may quote a number.
