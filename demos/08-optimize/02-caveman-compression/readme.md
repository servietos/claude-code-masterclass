# Compress Context with the Caveman Technique

Every message sent to Claude includes your CLAUDE.md as context. With five developers running twenty turns per session and twenty sessions per sprint, a 1,700-token CLAUDE.md burns through over three million tokens before a single line of feature code is shipped. The words that pad your instructions carry the same per-token cost as the words that drive the actual work.

Caveman mode is a rewriting discipline: strip articles, copulas, hedges, and politeness scaffolding while keeping every rule intact. The rule survives; only the wrapper is removed. A 68% reduction in a context file translates directly to a 68% reduction in every context window it appears in, multiplied across every turn, every session, every developer.

This demo walks through measuring that cost on a real TypeScript Fastify project, compressing the CLAUDE.md, and verifying that no rule was lost in the process.

## Set up the project

The starter project ships in [caveman-compression/](caveman-compression/) with `CLAUDE.verbose.md`, the `count-tokens.ts` helper, and a Fastify API under `src/`. Install and test it first:

```bash
cd demos/08-optimize/02-caveman-compression/caveman-compression
npm install
npm test
claude
```

Two Vitest tests pass.

## Measure the baseline

Use the token counter to establish the cost before any compression.

```text
Read count-tokens.ts (js-tiktoken, cl100k_base) and run it against CLAUDE.verbose.md.
Save the result to baseline.txt.
Show the compounding math: token_count x 20 turns x 20 sessions x 5 devs.
```

The direct command is `npm run token-count CLAUDE.verbose.md`, which reports 1725 tokens.

## Apply caveman mode

Rewrite your CLAUDE.md following the caveman rules to cut filler without losing intent.

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

## Verify parity

Confirm the compressed version contains all the same rules before swapping it in.

```text
Run count-tokens.ts against CLAUDE.caveman.md. Append result to baseline.txt.
Compare CLAUDE.verbose.md and CLAUDE.caveman.md rule by rule.
List any rule present in the original that is missing or weakened in the caveman version.
```

The reference rewrite in the solution folder lands at 559 tokens, a 68% reduction. The rule-by-rule verdict is a model judgement, so expect the wording of the parity report and the exact count to vary between runs; what must not vary is that every rule from the verbose file still appears.

The finished result, including `CLAUDE.caveman.md`, `baseline.txt`, and `parity-report.md`, lives in [caveman-compression-solution/](caveman-compression-solution/).

## The benefit, measured

Every one of these numbers comes from the two files in the solution folder: `count-tokens.ts` for the token counts, `parity-report.md` for the rule tally.

| Context attached to every single turn | Tokens | |
|---|---|---|
| `CLAUDE.verbose.md` | 1,725 | `████████████████████` |
| `CLAUDE.caveman.md` | 559 | `██████` |

| Measure | Verbose | Caveman | Change |
|---|---|---|---|
| Tokens (cl100k_base) | 1,725 | 559 | 68% smaller |
| Words | 1,465 | 362 | 75% fewer |
| Bytes on disk | 9,579 | 2,707 | 72% smaller |
| Tokens per sprint (5 devs x 20 turns x 20 sessions) | 3,450,000 | 1,118,000 | 2,332,000 saved |
| Rules enforceable | 35 | 35 | none lost |

The last two rows are the point of the technique: two thirds of the context bill disappears, and the rule-by-rule parity check still finds all 35 rules intact.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/usage` | Compare the session total of a verbose-context run against the same work under the caveman file |
| `/context` | Confirm the CLAUDE.md share of the context window actually shrank after the rewrite |
| `/rewind` | Restore the project files from before the caveman file was swapped in, if parity fails |

## Key Topics Covered in This Module

- [js-tiktoken on npm](https://www.npmjs.com/package/js-tiktoken): JavaScript port of OpenAI's tiktoken tokenizer, using cl100k_base encoding for Claude-compatible counts
- [Fastify documentation](https://fastify.dev/docs/latest/): official reference for route registration, plugin system, and type providers
- [Zod documentation](https://zod.dev): schema declaration and validation used for request/response types
