# Compress Context with Caveman Prompts

A CLAUDE.md is resent on every turn by every developer, so its word count is billed per message rather than once. You count the tokens in a verbose context file, rewrite it under caveman rules that strip the wrapper but keep every rule, then prove parity rule by rule before swapping it in. You end up with a context file around 56% smaller, a baseline showing the sprint-level cost, and a parity report accounting for all 40 rules.

------

The [caveman-compression/](caveman-compression) folder contains the starter files used in this demo. Open Claude Code inside that folder.

## Setup: Prepare the Project

Install the starter and confirm it is green before touching any context file:

```bash
cd demos/07-optimize-observability/02-caveman-compression/caveman-compression
npm install
npm test
claude
```

Expected result: `src/server.ts`, `src/users/router.ts`, `src/users/schema.ts`, `src/users.test.ts` in place and two Vitest tests passing. Start the API with `npm run dev` and hit `http://localhost:3000/users?page=1&size=2` to see the paginated envelope.

## Part A: Measure the Baseline

With the project in place, count tokens in the verbose CLAUDE.md and project the compounding cost:

```text
Read count-tokens.ts (js-tiktoken, cl100k_base) and run it against CLAUDE.verbose.md.
Save the result to baseline.txt.
Show the compounding math: token_count x 20 turns x 20 sessions x 5 devs.
```

The same count is available directly:

```bash
npm run token-count CLAUDE.verbose.md
```

It reports 1726 tokens, which is 3,452,000 tokens per sprint at 20 turns, 20 sessions, and 5 developers.

## Part B: Apply Caveman Mode

Rewrite CLAUDE.md following caveman rules:

```text
Rewrite CLAUDE.verbose.md as a caveman would say it.

Rules:
  - Short sentences. No articles (a, an, the). No copulas where droppable.
  - No hedging (please, kindly, generally, usually, it would be good to).
  - Imperatives only. "Do X" not "You should do X."
  - Preserve every rule: same enforceability, fewer words.
  - Keep all section headings, code fences, and file paths exactly.

Save to CLAUDE.caveman.md. Do not overwrite CLAUDE.verbose.md yet.
```

The reference rewrite in the solution folder lands at 766 tokens: a 56% reduction, verified with `npm run token-count CLAUDE.caveman.md`. Exact counts shift with wording, so treat 60-75% as the target band rather than a fixed number.

## Part C: Verify Parity

Confirm no rule was lost before swapping the file in:

```text
Run count-tokens.ts against CLAUDE.caveman.md. Append result to baseline.txt.
Compare CLAUDE.verbose.md and CLAUDE.caveman.md rule by rule.
List any rule present in the original that is missing or weakened in the caveman version.
Save the report to parity-report.md.
```

A good response names each rule by section heading, confirms it survives in the caveman version, and flags any softened imperative. This step is a model judgement, so the shape of the report varies between runs; the fixed expectation is that every rule from the verbose file is accounted for (the reference report in the solution folder enumerates 40). If Claude lists no differences, ask it to re-check the hedging rules specifically: those are the most likely to be preserved in spirit but weakened in enforceability.

The completed reference, with `CLAUDE.caveman.md`, `baseline.txt`, and `parity-report.md` filled in, is in [caveman-compression-solution/](caveman-compression-solution).
