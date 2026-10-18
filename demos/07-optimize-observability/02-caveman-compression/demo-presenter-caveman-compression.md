---
presents: demo-caveman-compression.md
budget: 4 min
beats: 4
---

# Present: Compress Context with Caveman Prompts

A context file is billed per turn, per developer, per session, so the number that matters is the sprint total. Four beats: the arithmetic, the five caveman rules, one section rewritten side by side, and the parity report that decides when the compression is finished.

------

**Shell:** the file inventory in the last question comes from `diff -rq -x node_modules -x package-lock.json caveman-compression caveman-compression-solution`; on Windows `diff` is an alias for `Compare-Object`, so run `Compare-Object (Get-ChildItem caveman-compression -Recurse -File -Name) (Get-ChildItem caveman-compression-solution -Recurse -File -Name)` instead.

## Beats

### Beat 1: The number that matters is 3,452,000, not 1726 (1 min)

**Open:** [`CLAUDE.verbose.md`](caveman-compression/CLAUDE.verbose.md) · [Part A: Measure the Baseline](demo-caveman-compression.md#part-a-measure-the-baseline)
**Say:** A context file is not read once, it is resent with every message, in every session, by every developer. It is the only text in the repository whose cost is charged per turn.

```text
Read count-tokens.ts (js-tiktoken, cl100k_base) and run it against CLAUDE.verbose.md.
Save the result to baseline.txt.
Show the compounding math: token_count x 20 turns x 20 sessions x 5 devs.
```

**Result:** [`baseline.txt`](caveman-compression-solution/baseline.txt), written by the Part A run and existing only in the solution

```text
File:   CLAUDE.verbose.md
Tokens: 1726
File:   CLAUDE.caveman.md
Tokens: 766
```

**Gotcha:** the file-level number is the wrong unit, and nothing about the rewrite is persuasive until the room has watched the multiplication happen.

### Beat 2: Caveman mode has five rules, and two of them are about not losing anything (1 min)

**Open:** [Part B: Apply Caveman Mode](demo-caveman-compression.md#part-b-apply-caveman-mode) · [readme.md](readme.md#apply-caveman-mode)
**Say:** Compression and summarisation are different operations, and only one is safe on a file of rules. This one targets the wrapper (articles, copulas, hedges, politeness) and never the instruction inside it.

```text
Rules:
  - Short sentences. No articles (a, an, the). No copulas where droppable.
  - No hedging (please, kindly, generally, usually, it would be good to).
  - Imperatives only. "Do X" not "You should do X."
  - Preserve every rule: same enforceability, fewer words.
  - Keep all section headings, code fences, and file paths exactly.
```

**Result:** the run wrote [`CLAUDE.caveman.md`](caveman-compression-solution/CLAUDE.caveman.md) beside the original, 766 tokens against 1726, and left `CLAUDE.verbose.md` in place.

**Gotcha:** the first three rules are the compression, the last two are the contract that stops it becoming a summary; writing to a second file is what makes the two comparable at all.

### Beat 3: Same rule, half the tokens (1 min)

**Open:** [`CLAUDE.verbose.md`](caveman-compression/CLAUDE.verbose.md) · the `## Error Handling` section, first paragraph
**Say:** Politeness and hedging read as care but carry no enforceability, and the model follows the imperative underneath either way. Ask of a rewritten line whether an instruction went missing, not whether it sounds thinner.

```text
It is important that you always remember to ensure that all route handlers allow Fastify to handle validation errors automatically via the Zod type provider integration, rather than writing custom try-catch blocks around validation logic. Please be sure to take care to understand that the `@fastify/type-provider-zod` package provides automatic request validation based on the schemas declared in the route's `schema` object, and that validation failures will automatically result in a 400 response with a descriptive error message. ...
```

**Result:** the same rule, with the heading byte-identical, in [`CLAUDE.caveman.md`](caveman-compression-solution/CLAUDE.caveman.md)

```text
Route handlers: let Fastify handle validation errors via Zod type provider. Never write custom try-catch around validation logic. `@fastify/type-provider-zod` validates from route `schema` object. Failures return 400 with descriptive message. Prefer this built-in validation everywhere. Fewer manual checks, fewer schema/logic mismatches.
```

**Gotcha:** "It is important that you always remember to ensure that" carries zero enforceability and opens 9 paragraphs of the verbose file; "It would be strongly advisable" opens 10 more.

### Beat 4: Parity is the gate, and a clean bill of health is the suspicious answer (1 min)

**Open:** [Part C: Verify Parity](demo-caveman-compression.md#part-c-verify-parity) · [readme.md](readme.md#verify-parity)
**Say:** A compression becomes trustworthy only once every rule has been accounted for one at a time, never by judging how the result reads. That audit is itself a model judgement.

```text
Run count-tokens.ts against CLAUDE.caveman.md. Append result to baseline.txt.
Compare CLAUDE.verbose.md and CLAUDE.caveman.md rule by rule.
List any rule present in the original that is missing or weakened in the caveman version.
Save the report to parity-report.md.
```

**Result:** [`parity-report.md`](caveman-compression-solution/parity-report.md), 40 rows, one per rule: 37 kept, 2 strengthened, 1 weakened

```markdown
| # | Original rule | Caveman rule | Status |
|---|---------------|--------------|--------|
| 17 | Let Fastify's built-in handler catch and format runtime errors. | Let Fastify's built-in error handler format them. | Kept ("catch" dropped) |
| 22 | Consider testing pagination explicitly on pagination routes. | Routes with pagination: test pagination explicitly. | **Strengthened** |
| 38 | Be sure to write commit messages that clearly describe purpose and intent, not the files modified. | Commit messages state purpose and intent, not file list. | **Weakened** (no modal; reads as description) |

40 rules compared. 37 kept at the same strength. 2 strengthened (advice became a must). 1 weakened (lost its modal).
```

**Gotcha:** if Claude reports no differences at all, send it back to re-check the hedging rules, which are the ones most likely to survive in spirit while losing their bite.

## If the room asks

| Question | Answer |
|---|---|
| Did any source file change? | No. The comparison reports three additions and nothing else: `baseline.txt`, `CLAUDE.caveman.md` and `parity-report.md`. `src/` and the tests are untouched. |
| Will my rewrite also land on 766 tokens? | No. Wording varies between runs, so treat 60-75% reduction as the target band. |
| Is this not just deleting rules to save tokens? | The parity report enumerates 40 rules and none is missing, which is exactly what it exists to prove. |
| Does `cl100k_base` match Claude's tokenizer exactly? | No, it is a stand-in for relative comparison; the ratio between the two files transfers, not the absolute count. |
| When do I overwrite `CLAUDE.verbose.md`? | After parity, never before. |
