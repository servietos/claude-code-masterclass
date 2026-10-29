# Run Parallel SDK Agents With Session Isolation

Build a code-review pipeline that runs three Claude Agent SDK sessions in parallel (a security reviewer, a performance reviewer, a style reviewer), each in its own isolated session. An orchestrator agent reconciles the three reports into a single verdict. Package the whole thing as a CI step.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **This lab costs money.** It needs an `ANTHROPIC_API_KEY`, and every `query()` call is a billed API request against your own account. This lab is heavier than Lab 01: Step 2 makes three calls, Step 3 makes six (two reviewers times three rounds), and Steps 4 and 5 add the orchestrator on top. Budget accordingly.

> **Prerequisite:** Complete [Lab 01](lab-01-sdk-embed-claude.md) through Step 5, the step that pairs `query()` with a Zod schema. This lab assumes you have used that typed-output pattern once already, and it reads the same key from `demos/10-sdk-managed-agents/.env`.

Work in [`02-sdk-parallel/sdk-review-pipeline/`](02-sdk-parallel/sdk-review-pipeline); the finished result is beside it in [`02-sdk-parallel/sdk-review-pipeline-solution/`](02-sdk-parallel/sdk-review-pipeline-solution). Open the solution when a step will not compile.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/10-sdk-managed-agents/02-sdk-parallel/sdk-review-pipeline
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `sdk-review-pipeline` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt, working from a session opened anywhere in the repo:

```text
In labs/10-sdk-managed-agents/02-sdk-parallel/sdk-review-pipeline create src/reviewers.ts with the security, performance and style reviewer configs ....
```

That works for every step whose result is just files, and here that is all of them: this lab writes no `.claude/skills/`, no `.claude/settings.json` hooks, no `.claude/commands/`, no `.claude/agents/` and no `.mcp.json`, so nothing depends on the launch directory. The terminal work does: `npm install` in Setup, `npm run step src/02-sdk-parallel.ts` and `npm run review target/auth.ts` all resolve from a shell sitting in `sdk-review-pipeline/`. Launch inside `sdk-review-pipeline` from Step 1 onward.

Launching inside the starter makes the repository a monorepo to this lab: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

The pipeline itself needs no Claude session: you run it with `npm run step src/<file>.ts` and later `npm run review`, and the SDK opens its own sessions from inside your Node process. The session above is simply where you write and edit those programs, and this project is a folder of its own beside Lab 01's.

---

## Setup: Open the Starter

The starter sits under `02-sdk-parallel/`, beside the reference solution and separate from Lab 01's project under `01-sdk-embed/`. It ships the dependency manifest, the compiler options, a `.gitignore` and the file the reviewers will review. Everything under `src/` is yours, from Step 1 onward.

Every command below runs inside `sdk-review-pipeline/`, the folder the session above is open in. Both lines run unchanged in git-bash and PowerShell.

```bash
npm install
npm ls --depth 0
```

Expected output:

```text
sdk-review-pipeline@1.0.0 ...\02-sdk-parallel\sdk-review-pipeline
├── @anthropic-ai/claude-agent-sdk@0.3.302
├── @types/node@26.1.2
├── dotenv@17.4.2
├── tsx@4.23.5
├── typescript@7.0.2
└── zod@4.4.3
```

No API key lives in this folder, because there is none to copy in. Every entry point you write starts with the same loader and reads the module's shared file:

```ts
import { config } from "dotenv";
import { fileURLToPath } from "node:url";

config({ path: fileURLToPath(new URL("../../../../../demos/10-sdk-managed-agents/.env", import.meta.url)), quiet: true });
```

The five `../` steps climb from `src/` past `sdk-review-pipeline`, `02-sdk-parallel`, `10-sdk-managed-agents` and `labs` to the repository root, then descend into `demos/10-sdk-managed-agents/`. Nothing has to be exported into the shell.

The shipped `tsconfig.json` carries an explicit `include`, and that line is load-bearing:

```json
{
  "include": ["src/**/*.ts"]
}
```

The compiler options set `rootDir: "src"`, so without it the default `**/*` glob sweeps `target/auth.ts` into the program and `npm run build` dies with `TS6059: File 'target/auth.ts' is not under 'rootDir'`.

The shipped `package.json` already carries every script the steps use, including the `review` script Step 5 wires to the CLI:

```json
{
  "scripts": {
    "build": "tsc",
    "step": "tsx",
    "review": "tsx src/05-cli.ts",
    "typecheck": "tsc --noEmit"
  }
}
```

Note there is no `--env-file` on either script. Each entry-point program starts with the `config({ path: ... })` loader instead, which is what lets the exact same `review` script run both locally (where the `.env` is on disk) and in CI (where it is not, because it is gitignored and the key arrives as an environment variable).

The target file the reviewers will review ships in the starter as `target/auth.ts`, so there is no heredoc to translate for PowerShell. Open it and read it before Step 1:

```ts
import crypto from "crypto";

let cache: Record<string, string> = {};

export function hashPassword(pw: string): string {
  if (cache[pw]) return cache[pw];
  const salt = "static-salt-1234";
  const h = crypto.createHash("md5").update(pw + salt).digest("hex");
  cache[pw] = h;
  return h;
}

export async function loginUser(email: string, password: string, db: any) {
  const user = await db.query("SELECT * FROM users WHERE email = '" + email + "'");
  if (!user) return null;
  return user.password_hash === hashPassword(password) ? user : null;
}

export function validateSession(token: string): boolean {
  return token.length > 10;
}
```

This file has deliberate problems in all three review categories: SQL injection (security), an unbounded cache (performance), and weak session validation plus a `db: any` (style and correctness). Each reviewer should find their own slice.

**Expected result:** `npm ls` lists the SDK, `dotenv`, `zod` and `tsx`, and `target/auth.ts` carries issues spanning the three review dimensions. There is no `src/` yet; Step 1 creates it with the first file.

---

## Step 1: Define the Three Reviewer Configs

**Goal:** Each reviewer needs a sharp, focused system prompt that constrains it to its dimension. Sharper prompts mean less overlap, which means cleaner reconciliation.

**Prompt:**

```text
Create src/reviewers.ts that exports three reviewer configurations as typed
objects, each with: name, systemPrompt, and reviewerSchema (a Zod schema for
that reviewer's output).

Reviewer 1, security:
  systemPrompt: "You are a security code reviewer. Focus exclusively on security
  issues: injection vulnerabilities, weak cryptography, missing authentication
  checks, insecure storage of secrets, weak session validation. Ignore
  performance and style, other reviewers cover those. Be specific: cite the line
  number and the exact attack scenario."

Reviewer 2, performance:
  systemPrompt: "You are a performance code reviewer. Focus exclusively on
  performance issues: unbounded data structures, missing pagination, N+1
  queries, blocking calls in hot paths, missed caching opportunities or caches
  that grow without bound. Ignore security and style. Cite line numbers and
  quantify the impact when possible."

Reviewer 3, style:
  systemPrompt: "You are a code-style and correctness reviewer. Focus on type
  safety (any, unknown, loose types), naming, dead code, incorrect control flow,
  and broken edge-case handling. Do NOT report security or performance issues,
  those are covered. Cite line numbers."

The schema differs per reviewer only in the `reviewer` literal, so build it with
a small generic helper, so the logic is written once:

  const FindingSchema = z.object({
    line: z.number().int().nullable(),
    severity: z.enum(["critical", "high", "medium", "low"]),
    summary: z.string(),
    recommendation: z.string(),
  });

  function reviewSchema<T extends "security" | "performance" | "style">(name: T) {
    return z.object({
      reviewer: z.literal(name),
      findings: z.array(FindingSchema),
      overall_verdict: z.enum(["block", "comment", "approve"]),
    });
  }

Also export a shared helper the later steps reuse:

  export function parseJsonBlock(raw: string): unknown {
    const text = raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "");
    return JSON.parse(text);
  }

Export the three configs individually and as a `reviewers` array.
```

Do not try to write `z.literal("security" | "performance" | "style")`. That is a type-level union sitting in a value position, so TypeScript reads the `|` as bitwise OR on strings and the line never even reaches Zod: it fails with `TS2362` and two `TS2363` errors. One literal per reviewer, or `z.enum([...])`, are the two valid spellings.

**Expected result:** A `src/reviewers.ts` exporting three reviewer configurations. Each system prompt is narrow and explicit about what it does and does not cover, and each schema pins its own `reviewer` literal so a mislabelled response fails validation.

---

## Step 2: Run the Three Reviewers in Parallel

**Goal:** Three independent Claude Agent SDK sessions, started simultaneously, completing in parallel. Each gets the same target file but its own system prompt.

**Prompt:**

```text
First create src/run-reviewer.ts, exporting one reusable function so Step 5 does
not have to duplicate it:

  export async function runReviewer(config, filePath, fileContents)

It should:
  1. Record Date.now() at the start.
  2. Call query() with options: { systemPrompt: config.systemPrompt, tools: [] }
     and a prompt that spells the return shape out literally, including the
     reviewer literal, because nothing else in the request tells the model what
     field names to use:

       "Review the following file. Return ONLY JSON, no prose and no code fence, matching exactly this shape:\n" +
       '{"reviewer":"' + config.name +
       '","findings":[{"line":number|null,"severity":"critical"|"high"|"medium"|"low","summary":string,"recommendation":string}],"overall_verdict":"block"|"comment"|"approve"}' +
       "\n\n<file path='" + filePath + "'>\n" + fileContents + "\n</file>"

     Setting tools: [] keeps the reviewer from wandering off and reading the
     filesystem, it only sees the text you handed it.
  3. Accumulate assistant text blocks, and capture message.total_cost_usd from
     the result message.
  4. Validate with config.reviewerSchema.parse(parseJsonBlock(text)).
  5. Return { reviewer, review, costUsd, durationMs }.

Then create src/02-sdk-parallel.ts that:
  1. Starts with the dotenv loader from Setup.
  2. Reads target/auth.ts and mkdirSync("results", { recursive: true }).
  3. Maps the reviewers array through runReviewer and awaits Promise.all,
     so all three sessions are in flight at once.
  4. Writes each validated review to results/<reviewer>.json.
  5. Logs per-reviewer findings count, verdict, cost and duration.
  6. Logs total wall-clock time AND the sum of the individual durations, so the
     parallelism is visible as a number.
```

Writing the shape into the prompt is the part that is easy to skip and expensive to debug. The three system prompts from Step 1 say what each reviewer should look for and leave the reply shape unspecified, so a prompt that only asks for "the schema specified by your system prompt" leaves the model free to invent field names. It usually guesses `reviewer` and `findings` correctly and then returns `description` where the schema says `summary`, or a verdict outside the enum, and `config.reviewerSchema.parse` throws a `ZodError` listing every mismatched path.

Because the three reviewers run under `Promise.all`, one reviewer guessing differently takes the whole run down. The Zod schema validates the reply; only the prompt can specify it.

Run:

```bash
npm run step src/02-sdk-parallel.ts
```

**Expected result:** Three JSON files under `results/`, and six log lines. The security reviewer should find the SQL injection and the MD5-with-static-salt hashing, the performance reviewer the unbounded `cache`, and the style reviewer the weak `validateSession` and the loose `db: any`. Exactly which findings each model reports, and how many, is not deterministic.

What is structural, and what you should check, is the last two log lines: wall clock comes out close to the slowest single reviewer, well under the sum of all three.

The verified run logged 7, 7 and 6 findings at 29.4s, 45.0s and 24.5s, for a 45.0s wall clock against a 98.8s sum, so the three sessions cost a little over a third of what running them one after another would have.

---

## Step 3: Verify Session Isolation

**Goal:** Confirm the three sessions are independent, with no context leaking between them. Without isolation the parallel pattern is unsafe, because one reviewer's input could steer another's output.

The design detail that makes this a real test: the security reviewer gets a copy of the file **with** the canary appended, and the performance reviewer gets the **original, unmodified** file. If both reviewers read the same canary-bearing text, a 'foxglove' hit would just mean the performance reviewer read its own input, which proves nothing. Split the inputs and a hit can only mean cross-session contamination.

**Prompt:**

```text
Create src/03-isolation-test.ts that:

  1. Starts with the dotenv loader from Setup, and defines const CANARY = "foxglove".
  2. Reads target/auth.ts into baseContents.
  3. Builds cannedContents = baseContents + a trailing line:
     "// CANARY: if any other reviewer mentions the word 'foxglove', the sessions are not isolated."
  4. Runs three rounds. Each round awaits Promise.all of:
       runReviewer(securityReviewer, filePath, cannedContents)
       runReviewer(performanceReviewer, filePath, baseContents)
     The performance reviewer must receive baseContents, the unmodified file.
  5. After each round, JSON.stringify the performance review, lowercase it, and
     check whether it includes the canary. Print PASS if absent, FAIL if present.
  6. Print the tally and exit 0 if all three rounds passed, 1 otherwise.
```

Run:

```bash
npm run step src/03-isolation-test.ts
```

**Expected result:** `isolation: 3/3 PASS` and exit code 0. The canary never crosses a session boundary, because each `query()` call opens a fresh session and there is no shared context unless you explicitly pass `options.resume`. To see the test actually bite, temporarily hand `cannedContents` to the performance reviewer too and re-run: the tally drops and the script exits 1.

---

## Step 4: Orchestrator Agent

**Goal:** A fourth Claude session whose only job is to reconcile the three reviewer outputs into one merged verdict. It never re-reads `target/auth.ts`; it reads only the three reviewer reports.

**Prompt:**

```text
Create src/orchestrate.ts exporting the reusable pieces, then a thin
src/04-orchestrator.ts entry point on top.

In src/orchestrate.ts:
  1. Define and export OrchestrationSchema:
       z.object({
         deduplicated_findings: z.array(z.object({
           line: z.number().int().nullable(),
           severity: z.enum(["critical", "high", "medium", "low"]),
           summary: z.string(),
           recommendation: z.string(),
           found_by: z.array(z.string()),
         })),
         contradictions: z.array(z.string()),
         verdict: z.enum(["block", "comment", "approve"]),
         rationale: z.string(),
       })
  2. Export VERDICT_EXIT_CODES = { approve: 0, comment: 1, block: 2 }.
  3. Export async function orchestrate(reviews) that calls query() with
     systemPrompt: "You are a code review orchestrator. Three reviewers have
     produced findings on a file. Your job is to (a) deduplicate findings that
     overlap across reviewers, (b) rank by severity, (c) issue a single overall
     verdict for the PR. Reviewers can be wrong, if one reviewer's finding is
     contradicted by another or seems mistaken, flag it. Return ONLY JSON."
     and options tools: []. The user prompt embeds all three reviewer JSON blobs
     and restates the exact return shape. Accumulate the assistant text, then
     OrchestrationSchema.parse(parseJsonBlock(text)).
  4. Export printSummary(result): the top 5 findings with severity, line,
     summary and found_by, then any contradictions, then verdict and rationale.

In src/04-orchestrator.ts:
  1. Start with the dotenv loader from Setup.
  2. Load results/security.json, results/performance.json, results/style.json.
  3. Call orchestrate(), write results/orchestrated.json, call printSummary().
```

Splitting the logic into `orchestrate.ts` keeps Step 5 a thin CLI that reuses it.

Run:

```bash
npm run step src/04-orchestrator.ts
```

**Expected result:** A `results/orchestrated.json` plus a readable summary in the terminal. Findings that more than one reviewer raised are collapsed into a single entry with `found_by` naming each reviewer that flagged it: on the verified run the SQL injection came back `found_by: security, performance` and the unbounded cache `found_by: performance, security, style`. The `contradictions` array is where the orchestrator earns its keep, calling out where one reviewer over-rated or misread a line the others read differently.

The verdict is the orchestrator's judgement, so treat it as a branch the model chooses. `block` means it considers at least one finding a merge stopper, `comment` that the findings are worth raising without gating the merge, `approve` that nothing rose to either. Given how broken `target/auth.ts` is, `block` is what you should expect and what the verified run returned, but the de-duplication and the severity ranking behind it are a model's call and can vary between runs.

---

## Step 5: Package as a CI Step

**Goal:** Wrap the whole pipeline as one CLI invocation that takes a file path, runs the three reviewers plus the orchestrator, and exits with a code derived from the verdict.

**Prompt:**

```text
Create src/05-cli.ts that:

  1. Starts with the dotenv loader from Setup.
  2. Reads the target file path from process.argv[2]. If it is missing, print
     "usage: npm run review <file>" to stderr and exit 1.
  3. Reads the file and ensures results/ exists.
  4. Runs the three reviewers in parallel via Promise.all over runReviewer,
     reusing src/run-reviewer.ts unchanged.
  5. Writes each review to results/<reviewer>.json.
  6. Calls orchestrate() on the three reviews, writes results/orchestrated.json,
     and calls printSummary().
  7. Exits with VERDICT_EXIT_CODES[result.verdict]: 0 approve, 1 comment, 2 block.
```

Run the CLI locally:

```bash
npm run review target/auth.ts
echo "exit code: $?"
```

From PowerShell the exit code is in `$LASTEXITCODE`, while `$?` holds a boolean:

```powershell
npm run review target/auth.ts
"exit code: $LASTEXITCODE"
```

Now add `.github/workflows/sdk-review.yml` so the same CLI runs on every PR:

```yaml
name: SDK Review

on: pull_request

jobs:
  review:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: sdk-review-pipeline
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - run: npm ci
      - name: Run SDK review pipeline
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          EXIT=0
          while IFS= read -r file; do
            echo "::group::Review $file"
            npm run review "../$file" || EXIT=$?
            echo "::endgroup::"
          done < <(git diff --name-only "origin/${{ github.base_ref }}...HEAD" | grep -E '\.(ts|tsx|js)$' || true)
          exit "$EXIT"
```

Five details in that workflow are load-bearing, and each one is a way the obvious version silently does nothing:

- `EXIT=0` before the loop, fed by **process substitution**, which keeps the loop in the current shell. A `while read` on the right-hand side of a pipe runs in a subshell, so an `EXIT=$?` set inside it is discarded the moment the subshell ends and the final `exit` returns 0 no matter how many files blocked. The check would pass forever.
- `fetch-depth: 0`, because `actions/checkout` defaults to a depth-1 clone and `git diff` against a branch that was never fetched just errors.
- `origin/${{ github.base_ref }}` so the diff follows whatever branch the PR targets.
- `working-directory: sdk-review-pipeline`, because the project sits in its own folder, so `npm ci` and `npm run` have to be told where to look. The `../$file` prefix compensates for the fact that `git diff --name-only` reports paths relative to the repo root.
- `npm run review` with no `--env-file`. There is no `.env` in a CI checkout, so the `config({ path: ... })` call finds nothing and returns quietly; the key arrives through the step's `env:` block and is already on `process.env` before the script starts. `--env-file` would instead abort the run with `node: .env: not found` and exit 9.

You will also need to add `ANTHROPIC_API_KEY` as a repository secret under Settings, Secrets and variables, Actions.

**Expected result:** The CLI prints the orchestrated summary and exits with the code the verdict maps to: `0` when the orchestrator approves, `1` when it wants comments, `2` when it blocks. The verdict comes from a model, so the exit code follows its judgement; on `target/auth.ts` the verified run blocked and exited `2`, which is what a file with an injection and a no-op session check should produce. On a PR, the workflow reviews every changed TypeScript or JavaScript file and fails the check if any of them come back `block`. You now have a multi-agent SDK pipeline in CI: three specialist reviewers, one orchestrator, one exit code.

---

## What You Just Practised

| Mechanic | Step | Why it matters |
|---|---|---|
| Per-reviewer system prompts and per-reviewer Zod literals | 1 | Sharp prompts produce sharp findings, and the schema catches a mislabelled reply |
| `Promise.all` over `query()` calls | 2 | Parallelism, where wall clock equals the slowest session's time |
| Canary test with split inputs | 3 | Proves the SDK gives each session its own context |
| An orchestrator agent that reads other agents' outputs | 4 | The reconciliation pattern for any multi-agent system |
| A CLI wrapper with semantic exit codes | 5 | A drop-in CI step that runs N agents and produces one verdict |
| GitHub Actions integration | 5 | The pipeline as a PR gate on every change |

This finishes the Agent SDK half of Module 10. Across these two labs you can embed Claude into your own program ([Lab 01](lab-01-sdk-embed-claude.md)), then scale that to multiple agents running in parallel with reconciliation (Lab 02). The [`agent-sdk-dev`](https://github.com/anthropics/claude-code/tree/main/plugins/agent-sdk-dev) plugin can scaffold these patterns for new projects, but the discipline of session isolation and orchestration is yours. [Lab 03](lab-03-agent-codebase-triage.md) hands the same loop to Managed Agents.
