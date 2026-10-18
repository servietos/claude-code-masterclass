# Lessons

## class-planning evaluate: don't infer the labs rule from the repo

**Mistake (2026-05-14):** When re-running the `evaluate` workflow, I changed `labs` from `done` → `planned` for 7 modules (05, 06, 08, 09, 10, 11, 12) based on a guessed rule ("topic subfolders count as the labs surface"). That broke the existing, correct values in `class-state.json`.

**Why it was wrong:** No module has a `labs/` folder, so the documented rule never fires. The actual labs surface is not derivable from `demos/<n>/` alone. The user maintains the labs values out-of-band, and they were already correct before my eval.

**Rule for the future:**
- Re-evaluate only `theory`, `demos`, and `slides` against the repo when running `evaluate`. Those three have clean rules: topic readmes for theory/demos, `pptx/*` for slides.
- **Preserve existing `labs` values verbatim.** Only change `labs` when the user explicitly instructs the new value, or when a `labs/` folder is added and the documented rule starts matching.
- If a guess about a rule is needed, ask the user first instead of writing a new state file.

## Demo guides live in their topic folder, not the module root

**Change (2026-07-22):** All 31 module-root demo guides moved into the topic folder they teach, renamed from `NN-demo-<slug>.md` / `demo-NN-<slug>.md` to `demo-<slug>.md`. Ordering now comes from the numbered topic folder, so the guide carries no number of its own.

**Rule for the future:**
- A demo guide sits beside the `readme.md` of the topic it teaches: `demos/NN-<module>/II-<topic>/demo-<slug>.md`. Lab guides stay at the module root as `lab-NN-<slug>.md`.
- Write a guide's relative links from the topic folder: a runnable project in the same topic is `<slug>-py/`, a sibling topic is `../II-<topic>/`.
- The module `readme.md` indexes demos in a two-column `| Topic | Demo |` table, one row per demo under its strongest topic fit.

## Placing content: derive from existing links before asking

**Pattern (2026-07-22):** Deciding which topic owned each of 31 demos looked like 31 judgment calls. Three signals in the repo answered 27 of them: the relative links inside each guide pointing at its code folder, the `See [...](../<guide>.md)` backlinks in topic readmes, and the module readme demo tables. Only 4 were genuinely ambiguous.

**Rule for the future:** Before asking the user to place or classify a batch of files, mine the existing links in both directions and answer everything they determine. Ask one batched question for the residual, never a question per file.

## Moving markdown: sweep links and the generated artifacts

**Mistake (2026-07-22):** The restructure was reported as verified after checking that every relative link resolved, but the dashboard scripts (`dashboard/evaluate.py`, `dashboard/render-dashboard.py`) match demo files by regex at the module root. After the move they found zero demos, silently regressing module status to `planned`.

**Why it was wrong:** Link integrity is only half of a move. Any script, template, or generated file that discovers content by path or filename pattern is equally coupled to the layout, and it fails silently rather than at a broken link.

**Rule for the future:**
- After moving content, grep for the old paths AND the old filename patterns in scripts, `dashboard/`, skill templates, and workflow files, not only in Markdown.
- Regenerate generated artifacts from their source of truth (`python dashboard/render-dashboard.py`) instead of hand-patching the generated HTML, then confirm the entry count is what you expect.
- When a move invalidates a convention encoded in a skill (here `create-guide`'s "module root" placement rule), update the skill in the same session or the next run silently reintroduces the old layout.

## Check the global skill before treating a local convention as new

**Pattern (2026-07-22):** Moving demo guides into topic folders looked like a new local convention. The global `create-class` skill had mandated exactly that placement for a while; only the repo-local copy still said "module root". The session was the repo catching up to a proven global rule, not inventing one.

**Rule for the future:** Before authoring a rule locally, diff the local skill against `~/.claude/skills/<name>/` (`diff -rq`). If global already has the answer, pull it down instead of writing a second version. Push up only the genuinely new part.

## A convention split across a doc and a script breaks silently

**Pattern (2026-07-22):** Global `create-guide` said guides live in the topic folder while the global dashboard templates only scanned the module root. The two halves of one convention disagreed, so any class repo following the doc reported zero demos with no error.

**Rule for the future:** When a convention is enforced in prose AND consumed by a script, change both together and add a test that pins the behavior (`test_demos_done_topic_subfolder`). A convention with no test is a convention that silently rots.

## Batch `sed -i` on Windows rewrites line endings

**Pattern (2026-07-22):** Looping `sed -i` over a file list touched every file in the list, including ones with no match. On a CRLF working tree that rewrote line endings, so `git status` showed files as modified with an empty content diff.

**Rule for the future:** After a batch `sed -i` sweep, drop the no-op edits: for each modified file, `git checkout --` it when `git diff --numstat` reports no changed lines. Keeps the diff to what actually changed.

## Demos need a starter and a solution folder

**Pattern (2026-07-22):** Verifying every demo under `demos/05-cli` meant installing dependencies and running builds inside the folders the learner starts from, which left `node_modules` and a lockfile in a starter. The user asked mid-run for runs to happen in a `<demo>-solution` folder so starters stay clean.

**Rule for the future:** A runnable demo folder is the starter and stays pristine (no installed dependencies, no lockfile, no build output). Copy it to a sibling `<starter>-solution/` and run there. Fix broken assets in both: the starter must be a correct starting point, the solution carries the worked-out result. State the convention once in the module `readme.md` and name the solution at the end of each guide. Recorded in `CLAUDE.md` and in `create-class`'s `run-demo`, `scaffold`, and `create-guide` leaves.

## Verifying an agent-driven demo: separate plumbing from model behaviour

**Pattern (2026-07-22):** The parallel-worktree and CI-gate demos call `claude -p`. Running them for real is slow, costly and non-deterministic, so the scripts were proved with a stub `claude` earlier on `PATH` while single headless calls were run for real once.

**Rule for the future:** Prove script plumbing (command substitution, backgrounding, `wait`, exit codes, JSON parsing, merges, cleanup) with a PATH-shadowed stub, prove the envelope with one real bounded `claude -p`, and report anything else (interactive REPL steps, GitHub Actions jobs, multi-agent runs) as not executed with the reason. A step whose outcome is a model judgement never gets a promised exit code in the guide.

## Silent script defects that a reading pass misses

**Pattern (2026-07-22):** Two shipped scripts looked correct and were not: `lint-with-claude.sh` was missing command substitution, so its `grep` ran against an empty string and the gate always passed, and `policy-gate.sh` never blocked anything while the guide claimed it did.

**Rule for the future:** Never accept a gate, hook, or exit-code script from reading alone. Execute every branch: feed a hook its real stdin payload and assert the exit code (exit 2 blocks), and force each exit path (0/1/2) with a stub. A gate that cannot fail is worse than a missing gate.

## Demo setup must not git init inside another demo

**Pattern (2026-07-22):** Two guides told the learner to `cd` into another topic's starter and run `git init`, which creates a nested repository plus `node_modules` and worktrees inside the course repo.

**Rule for the future:** When a demo needs its own git history, the setup copies the project outside the course repo first, then runs `git init` and the first commit there. Any step that reads git history (`git log`, `git branch --show-current`) needs that commit to exist earlier in the same guide.

## An adversarial recheck pass is worth its cost

**Pattern (2026-07-22):** The verification workflow ran one agent per topic and then an independent agent that re-ran the same guides from a clean state without trusting the first report. The recheck caught overclaims and regressions the first pass introduced.

**Rule for the future:** For "make all of this work" sweeps, pipeline every unit through find-then-independently-verify rather than trusting a single pass, and require each fix to be re-executed before it counts as fixed. Give the fan-out hard ground rules up front: throwaway clones under the scratchpad, bounded loops, no commits, at most one real paid call per unit.

## Course content asserts harness behaviour that expires

**Pattern (2026-07-22):** Transferring the 05-cli conventions to modules 06, 07 and 08 turned up four teaching claims that the installed CLI no longer supports: `think hard about this:` as a thinking trigger (2.1.217 recognises `ultrathink` plus `/effort` and `MAX_THINKING_TOKENS`), `/agents` described as a live editor (removed in 2.1.198), `/permissions` described as editing agent frontmatter, and a `permissions: allow/deny` block in sub-agent frontmatter that the loader silently strips.

**Rule for the future:** Any claim about harness behaviour (a keyword, a slash command, a frontmatter key, a settings shape) is verified against the installed binary and the current docs before it ships, and re-verified whenever a module is touched. Silently-stripped config is the dangerous class: it reads as protection and provides none. Encoded as brand-voice rule 7.

## Teaching material inherits the repo's own config defects

**Pattern (2026-07-22):** Five of six topics in `demos/07-subagents` shipped an unsupported `permissions:` block and a mapping-form `mcpServers` because the guides quote this repo's own `.claude/agents/*.md`. The guides were not independently wrong; they faithfully reproduced a broken source.

**Rule for the future:** When a guide quotes the repo's live configuration, validate the source file, not just the excerpt. Fixing the excerpt alone leaves the defect shipping from two places and they drift apart. Sub-agent frontmatter, hook JSON, and settings snippets all belong to this class.

## Two authored rules that contradict each other produce inconsistency at scale

**Pattern (2026-07-22):** `CLAUDE.md` says every code fence declares a language while `create-class/references/create-guide.md` requires bare prompt fences. Independent agents resolved the conflict in opposite directions in neighbouring topics, so the contradiction propagated as inconsistency instead of surfacing as an error.

**Rule for the future:** A contradiction between two authored rules is a defect in the rules, not a judgement call for whoever hits it. When one is found, resolve it centrally in the same session and state the winner in both places; a fan-out over many units will otherwise multiply it.

## Demo folders that ship a .claude tree join the host repo's roster

**Pattern (2026-07-22):** `demos/08-optimize/03-autoresearch-loop` ships `.claude/skills/release-notes/` as demo content. The course repo's harness discovers it as a real, directory-scoped skill, and copying the starter into a solution folder registered it a second time.

**Rule for the future:** Demo content under `.claude/skills/` or `.claude/agents/` becomes live configuration of the repo that hosts it, and the starter/solution split doubles it. Decide deliberately per demo: keep the demo config out of `.claude/` naming, or state in the topic readme that the roster entry is demo content. Recorded in `create-class/references/run-demo.md`.

## git status is not a purity check when something else is committing

**Pattern (2026-07-22):** Two commits appeared mid-run from outside the workflow and swept the new solution folders into history. `git status` then reported clean, which is exactly what a passing starter-purity check looks like, so the check silently stopped proving anything.

**Rule for the future:** Verify starter purity against the filesystem (`find <starter> -name node_modules -o -name .venv -o -name '*.lock'`), not only against `git status`. Treat a suspiciously clean tree during a long run as a signal to check `git log` before trusting any git-based assertion.

**Recurrence (2026-07-24):** It happened again, in the other direction: a concurrent writer added 32 files across `labs/` and `.devcontainer/` (including staged `A` entries) during a 29-minute workflow that touched only `demos/`. This time `git status` was too dirty rather than too clean, which is equally useless: it mixed two sessions' work into one undifferentiated list. The attribution that worked was mtime comparison, `ls -l --time-style=+%m-%d_%H:%M` across a file the run definitely changed and one it definitely did not; the run's own files clustered at 19:38-19:39 while the foreign ones carried 19:52-19:55. Since the first fix did not hold, treat this as standing procedure: on any multi-agent run, record the start time, and attribute changed files by mtime before reporting what the run did. Never describe `git status` output as "the run's changes".

## A subagent's "I verified it against the binary" is not proof

**Pattern (2026-07-22):** Two independent agents reported that sub-agent frontmatter `mcpServers` must be a YAML list and that a mapping form is silently dropped, citing a grep of the installed `claude.exe`. One of them rewrote a guide to teach the list form. The official docs say the opposite: an entry is either a plain server name or an inline definition keyed by the server name, which is the mapping form the repo already shipped. A control grep of that binary returns zero hits for every search term, because the payload is packed, so the claimed evidence could not have existed.

**Rule for the future:** Claims about harness behaviour are settled against the documentation or an executed experiment, never against a subagent's summary of a binary grep. Two agents agreeing is correlation, not corroboration: they read the same wrong source. When a report contradicts shipped, working configuration, check the docs before editing the guide, and check whether the "evidence" reproduces.

## Restoring deleted config means re-deriving it, not reinstating it

**Pattern (2026-07-24):** `.devcontainer/` was deleted in `a6696a0` ("Go live #928") and recovered from `a6696a0^`. The restored files dated from 2026-05 and had silently drifted from the repo: they still installed Azure Functions Core Tools, azurite and the Dev Tunnels CLI (zero references anywhere in the repo today) and were missing uv, Hugo, Terraform, docker-in-docker, and the Claude Code CLI itself. A verbatim restore would have built and run, which is what makes this failure mode expensive.

**Rule for the future:** Recover the old file for its structure, then re-derive its contents from the repo's current ground truth. For an environment config that ground truth is the set of project manifests: `find demos labs src -name '*.csproj' -o -name package.json -o -name requirements.txt -o -name pom.xml -o -name angular.json -o -name Dockerfile`. Every tool the config installs must map to a manifest that needs it, and every manifest must map to a tool. Drop the unmatched installs rather than carrying them forward. Check first whether the config provides the very thing the repo is about: the devcontainer for a Claude Code class had never installed `@anthropic-ai/claude-code`. Encoded as the global skill `devcontainer-from-repo`.

## Config cross-references and cleanup globs rot silently

**Pattern (2026-07-24):** Re-deriving the devcontainer surfaced two defects that had never thrown an error. `post-create.sh` ran `find /workspace -type d -name bin -exec rm -rf {} +`, which was harmless when written and now deletes `.venv/bin` in the container, breaking every Python virtualenv the course added since. And `devcontainer.json` set `esbenp.prettier-vscode` as the TypeScript default formatter while never listing that extension for installation, so format-on-save was a no-op for TypeScript.

**Rule for the future:** Two checks whenever an environment or tooling config is touched. First, scope every destructive glob to the directories it means and prune the generated trees explicitly (`-name node_modules -o -name .venv -prune`); a glob that was safe against the old repo is not evidence it is safe against this one. Second, verify that every identifier a settings block references (extension IDs, formatters, tasks, paths) is actually provided somewhere in the same config. Both defects are invisible at runtime, so they survive until someone re-derives the file. Full catalog in the global skill `devcontainer-from-repo/references/gotchas.md`.

## Use the Grep tool, not Bash grep -r, for content search in this repo

**Pattern (2026-07-24):** A `grep -rl` sweep over `demos labs src` to count tool references hit the 2-minute Bash timeout and returned partial output. The `-solution/` folders ship `node_modules` and `.venv`, so a recursive Bash grep walks tens of thousands of vendored files. The same questions answered instantly through the Grep tool, which uses ripgrep and skips gitignored trees by default.

**Rule for the future:** Content search goes through the Grep tool in this repo. Reserve the Bash tool for git plumbing, `find` over manifest filenames, and running commands. When Bash grep is genuinely needed, pass `--exclude-dir=node_modules --exclude-dir=.venv`. This refines the standing bash-over-PowerShell preference: it is about which shell, not about hand-rolling searches that a dedicated tool does faster.

## Git Bash on Windows silently breaks two verification steps guides assume

**Pattern (2026-07-24):** `run-demo` Step 6A requires proving a demo exits cleanly on Ctrl+C, and the skills packaging demo runs `zip -r`. Neither is executable here. `zip` is not on PATH at all (exit 127), and Windows does not raise a console CTRL_C_EVENT from a POSIX signal, so both `kill -INT <pid>` (returned rc=0, process ran to completion and exited 0) and `process.kill(process.pid, 'SIGINT')` (killed the process without ever invoking the listener) failed to exercise the handler. A control test with a trivial `process.on('SIGINT')` confirmed the platform, not the code, was the blocker.

**Rule for the future:** Before writing a verification step into a guide, confirm the command exists and the mechanism works on the target platform. A registered SIGINT handler that compiles is not a verified SIGINT handler; report it as "handler registered, interrupt behaviour not verifiable on Windows" rather than claiming a pass. Prefer `powershell Compress-Archive` over `zip` in any guide that a Windows learner will run. Recorded in `create-class/references/run-demo.md` (Step 6A, plus the `zip` row in Step 6b).

## A tool that prints correct output and then crashes reads as a failed demo

**Pattern (2026-07-24):** `npx @modelcontextprotocol/inspector --cli --method tools/list` printed the complete, correct tool list for both MCP servers, then died on teardown with `Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c, line 76` and exit code 3221226505. The server was healthy; the crash is a libuv teardown bug in the inspector on Windows. Nothing in either guide warned about it, so the first thing a learner sees after a successful step is a native assertion dump.

**Rule for the future:** When a verified step ends in a crash or stack dump that does not affect the result, the guide must say so at that step, not only in troubleshooting. Judge a step by whether the payload arrived, and separate "the data was correct" from "the process exited cleanly" in both the report and the guide's expected result. Recorded in `create-class/references/run-demo.md` as new Step 6c.

## A floating "latest" plus a peer-dependency major bump makes a demo uninstallable

**Pattern (2026-07-24):** Both Agent SDK demos declared `"@anthropic-ai/claude-agent-sdk": "latest"` alongside `zod ^3.22.0`. The SDK had since moved to 0.3.219, which requires peer `zod ^4.0.0`, so `npm install` failed outright with ERESOLVE. The demos had not changed; the ecosystem moved underneath them. Type checking then surfaced a second layer of drift: `AssistantMessage` and `TextBlock` are no longer exported (they are `SDKAssistantMessage`, and the block types moved), and the package is ESM-only, so a CommonJS tsconfig cannot require it.

**Rule for the future:** A course demo never floats a dependency version. Pin the exact resolved version in the starter and keep the lockfile in the solution, so the demo a learner installs is the one that was verified. Treat "the guide is unchanged" as no evidence that the guide still works: any demo depending on a fast-moving SDK needs its install and typecheck re-run before a class, not just its prose reviewed. Recorded in `create-class/references/run-demo.md` (Step 9, plus ERESOLVE, ESM-in-CommonJS and renamed-export rows in the Step 8 error table).

## A stale local skill copy withheld exactly the guidance the work needed

**Pattern (2026-07-24):** Two .NET MCP server demos were built and verified while `.claude/skills/dotnet-conventions/` in this repo carried 2 reference files (`conventions.md`, `dotnet-cli.md`). The global copy at `~/.claude/skills/dotnet-conventions/` carries 14, including `dotnet-mcp.md`, and a different description that advertises MCP server development. The local manifest also advertised less than the global one, so nothing in the repo hinted that the MCP reference existed one tier up.

**Rule for the future:** Before doing domain work that a local skill nominally covers, `diff -rq ~/.claude/skills/<name> <repo>/.claude/skills/<name>` and check whether the global tier has leaves the local copy lacks. A thin local copy is not evidence that no guidance exists. Drift is invisible from inside the repo, because a skill advertises only what its own manifest lists.

**Addressed (2026-07-24):** Reconciled via `claude-learn`'s `skill-drift-audit`. Local now carries 13 references including `dotnet-mcp.md`; `file-import-ingest.md` and `azure-blob-storage.md` stay global-only because both are bound to another repo's paths and entities. The audit also caught two integrity defects that a file-by-file copy would have produced: a dangling router row on global and a merged leaf that had landed on one side only. Verify a reconcile with both checks, `diff -rq` AND every delegate-map row resolving on its own side; the second one is what catches a partial sync.

## A documented symptom with an invented cause survives every reading pass

**Pattern (2026-07-24):** `qr-mcp-app-cs/readme.md` stated that a plain browser GET returns HTTP 400 because "MCP clients must send the `Accept: application/json, text/event-stream` header". The symptom was real, the cause was fabricated, and the sentence reads as authoritative. Executing it showed error `-32000` with `Mcp-Session-Id header is required for GET and DELETE requests when the server is using sessions`, and sending the prescribed `Accept` header returned a byte-identical 400. A prose review would never have caught it.

**Rule for the future:** A stated cause is a testable claim, not narration. When a guide explains why something fails, reproduce the failure and confirm the stated remedy actually changes the outcome; a fix that does not change the response is the tell. Correcting the symptom text while leaving the wrong cause in place teaches the wrong mental model, and the same sentence had been copied into the solution folder, so both needed the fix.

## The folder number is authoritative for a module's H1

**Pattern (2026-07-24):** `demos/03-skills/readme.md` was titled "Module 4" and `demos/04-mcp/readme.md` was titled "Module 3", a mirror-image swap that had survived in both files. Fixing either one alone would have left two modules claiming the same number, so the pair had to be resolved together. Alongside it, `demos/03-skills/04-pubishing/` carried a folder-name typo that both index links reproduced into the learner's URL bar.

**Rule for the future:** Module and topic numbering lives in the folder name; every H1, index row, and cross-link derives from it. Check the whole set at once rather than per file, because numbering defects come in pairs and a single-file fix can create a collision. When a folder is renamed, sweep the links and re-run the generator that emits `dashboard/index.html`, never hand-edit the generated artifact.

## Python `read_text` normalizes CRLF, so line-ending detection lies

**Mistake (2026-07-24):** A script that stripped YAML frontmatter from 18 skill files tried to preserve line endings by sniffing them from the text: `nl = "\r\n" if "\r\n" in raw.split("\n")[0] + "\n" else "\n"`. `Path.read_text()` applies universal-newline translation, so `raw` never contains `\r\n` and the check always chose `\n`. Ten CRLF files were silently rewritten to LF. The verification that missed it used `grep -c $'\r'`, which reported the pre-edit counts and read as a pass; only `tr -cd '\r' | wc -c` against a backup exposed it.

**Why it matters:** the whole-file rewrite hides the real diff. `diff` reports `1,551c1,546` instead of the five removed lines, so a reviewer cannot see what actually changed, and on a CRLF working tree every touched file shows as modified.

**Rule for the future:**
- To preserve line endings in Python, read with `newline=''` (`open(p, newline='')` or `read_text(newline='')`), which disables translation and keeps `\r\n` visible. Never sniff line endings from text read in default mode.
- Verify line endings by counting bytes (`tr -cd '\r' | wc -c` and `tr -cd '\n' | wc -c`) against a pre-edit backup, not with `grep -c`.
- Back up before a batch rewrite and diff CR-normalized (`diff <(tr -d '\r' < a) <(tr -d '\r' < b)`) so content changes are separable from line-ending changes.
- **Correction, same session:** I first concluded that `sed -i` preserved CRLF and only the Python rewrite flattened it. That was wrong, and only looked true because every `sed`-touched file happened to already be LF. A later `sed -i` link fix on three CRLF files stripped every CR (42/40/274 CRs to 0). On Git Bash, assume `sed -i` flattens CRLF. Both tools re-serialize the file; neither is safe by default.
- Measure line endings before AND after every batch edit, not just after. Comparing a post-edit count against nothing proves nothing, which is how the first slip survived a verification pass.

## An unquoted colon-space silently invalidates skill frontmatter

**Pattern (2026-07-24):** Seven global skills had `SKILL.md` frontmatter that is not valid YAML, all from the same cause: a plain (unquoted) `description:` scalar containing a colon followed by a space, as in `via its blue-green leaf: triggers on ...` or `Add AI image generation via DeepInfra: FLUX-2 ...`. YAML reads `: ` inside a plain scalar as a nested mapping and errors with "mapping values are not allowed here". The config lint did not catch it because it checks for the presence of `name`/`description`, not that the block parses. One of the seven was self-inflicted earlier in the same session.

**Rule for the future:**
- Any skill or agent description containing `: `, or a leading `#`, `>`, `|`, `[`, `{`, `&`, `*`, must use a folded block scalar. Write `description: >-` and put the text on the following line indented two spaces. Quoting instead forces escaping every embedded `"`, which trigger-phrase lists are full of.
- Add a real YAML parse to the verification, not a key-presence grep: `yaml.safe_load` the frontmatter of every `SKILL.md` and assert non-empty `name`/`description` plus `name == folder`.
- A skill whose frontmatter fails to parse can disappear from the model's skill listing while still looking correct in the editor, so it fails exactly where it matters and nowhere else.

**Related correction:** the missing descriptions were misdiagnosed first as skills genuinely lacking a `description:` key. All 67 global skills had one. The observable symptom (no description in the listing) came from the unparseable frontmatter above. Diagnose from the file, not from the rendered listing.

## Byte-identical references do not make a skill redundant

**Mistake (2026-07-24):** Auditing 67 global skills, I reported that `banner-design` and `slides` were "fully contained in `design`" because every one of their `references/*.md` files was byte-identical to a file already in `design`. Acting on that would have discarded content. Probing the routers separately showed `banner-design/SKILL.md` had 45 distinctive lines present nowhere in `design` (a full art-direction and per-platform workflow), while `slides` genuinely had none.

**Rule for the future:** Duplication has to be measured per file, and a skill's manifest is a different file from its references. Probe the router body independently: take its lines over ~50 characters and test each against the whole candidate master. Identical leaves usually mean the leaves were copied; they say nothing about whether the router carries unique process. Absorb the router as its own reference unless the probe returns zero unique lines.

## Merging a skill into a reference deletes its discoverability

**Pattern (2026-07-24):** Consolidating 67 global skills to 53 moved 14 skill manifests into `references/<leaf>.md`. A reference carries no `description`, so every trigger phrase the absorbed skill owned stops matching the moment it moves. "Dockerize my .NET API" matched `docker-dotnet` before the merge and matches nothing after, unless the phrases are folded into the master.

**Rule for the future:**
- Every absorb is two edits, never one: move the body, then fold the leaf's trigger phrases into the master `description`. Capture the description before archiving, because the source folder is gone afterwards.
- Folding has a budget. Each fold grows the master description by 300 to 600 characters and dilutes matching for everything else in it, so merge only what genuinely shares a task. That is why host-agnostic containerization became its own `docker-images` master rather than folding into `deploy-hetzner-box`, whose description was already near 1800 characters after three folds.
- A merged description almost always gains a colon-space and must be a folded block scalar (`>-`), or the frontmatter stops parsing.

## Absorbing a file one directory deeper breaks its relative links

**Pattern (2026-07-24):** `sql-db-ensure/SKILL.md` linked to `../deploy-init/SKILL.md` and `../umbraco/references/umbraco-sql.md`. Absorbed to `sql-server/references/db-ensure.md` it sits one level deeper, so every `../` prefix now resolves one directory short. Nothing errors: the links just point at paths that do not exist.

**Rule for the future:** After any move that changes a file's depth, re-run a link resolver over the whole tree rather than only over the files edited by hand. Two checks separate real loss from intended edits: resolve every relative `.md` link from its own directory, and diff each moved body against a pre-move backup, classifying each missing line as an intended rewrite or an unexplained loss. Anything unexplained is a bug.

## Running a guide is the only way to know what it claims is true

**Pattern (2026-07-24):** Executing all 29 lab guides in solution folders produced 270 findings and 41 blockers. Reading them would have found almost none of it, because the defects are all of the form "this looks completely reasonable and does not work". The recurring classes, worth using as a checklist on any future guide audit:

- **Invented CLI surface that looks right.** `/plugin reload` (the real command is `/reload-plugins`), `ant whoami` (real is `ant auth status`), `specify init --integration claude` (real flag is `--ai`). Each is plausible enough that no reader would question it.
- **Unsupported frontmatter that fails silently.** `permissions:` with allow/deny on a subagent, and `env:` with `inherit`/`pass` for scoped secrets. Neither key exists, so the learner ships a security control that is decoration. This is the worst class because nothing errors.
- **A variadic flag eating the positional argument.** `claude -p --add-dir <dir> "prompt"` parses the prompt as a second directory and dies with "Input must be provided". The same happens with `--allowed-tools`.
- **Manifest in the wrong place.** `plugin.json` at the plugin root instead of `.claude-plugin/plugin.json`, so the plugin never loads.
- **Exit codes lost to a subshell.** A variable assigned inside a piped `while read` loop is discarded when the subshell exits, so a CI gate always exits 0 and can never fail a pull request.
- **Command substitution inside a double-quoted YAML string.** Backticks around a `gh issue create` example in a workflow heredoc made the runner execute it while building the prompt.
- **Unix-only commands in a Windows-primary repo.** `crontab`, `nohup`, `xargs -P`, bare `export VAR=`, and `chmod +x` handed to a learner with no note about git-bash or WSL.
- **Stale build output masking a broken build.** A committed `dist/` from an earlier run made `node dist/index.js` work locally while the documented build could not complete at all without a missing toolchain.

**Rule for the future:** Verify a guide by executing it, not by reading it. For every claim the guide makes, run the thing: check flags against `--help` and the live docs, parse every JSON and YAML block, feed hook scripts a real stdin payload and assert the exit code, drive MCP servers over a JSON-RPC handshake to capture their real tool names, and curl every URL. Anything that cannot be executed (a live session, a paid account, a browser) gets labelled not-executed with the reason, and its preconditions get verified instead. Never report as verified what was not actually run.

## "I cannot find it" is not "it does not exist"

**Mistake (2026-07-24):** A scout reported that one module's entire `ant beta:agents` CLI surface, its toolset id, and the model `claude-opus-4-7` were fabricated. I relayed that to the user as "appears fabricated". The follow-up audit against the real documentation showed the `ant` CLI is real and documented, and `claude-opus-4-7` is a real supported model. The guide's actual problem was different and more useful: the CLI is real but nearly every command in the lab is malformed against it, in 16 specific documented ways.

**Rule for the future:** Before calling content invented, check the vendor documentation for the exact surface. A negative search result is evidence about the search, not about the world. Frame the finding as "could not confirm X against source Y" until a source is actually read, because "fabricated" and "real but wrong in 16 ways" lead to completely different fixes: one throws the guide away, the other corrects it command by command.

## Verify agent-driven scripts with a stub on PATH, and assert the stub took effect

**Pattern (2026-07-24):** Several labs wrap `claude -p` in shell scripts whose logic (exit codes, sentinel tokens, JSON parsing, background polling) is worth proving but whose model output is not. Putting a stub `claude` executable earlier on PATH proved the plumbing end to end at zero cost: a PASS token gave exit 0, a FAIL token exit 1, neither token exit 2. The failure mode cost real money: passing a Windows-style path when prepending to PATH silently did nothing, so one live billed call ran before it was noticed.

**Rule for the future:** Separate what a script does from what the model decides, and stub the model. When prepending to PATH inside git-bash on Windows, convert with `cygpath -u` and then assert `which claude` actually resolves to the stub before running anything. A silent no-op on PATH looks identical to a working stub right up until the invoice.

## The Claude Code harness is project-scoped, and that breaks tutorials quietly

**Pattern (2026-07-24):** `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` are all read from the directory the session was launched in. Guides that had a learner build a harness inside a lab folder while sitting in a session opened at the repo root produced no hook, no skill, and no error at all. Three labs additionally instructed writing into the course repo's own `.claude/`, which would add live agents and skills to the reader's roster.

**Rule for the future:** Every guide that creates a harness artifact must state where to open Claude Code, and the answer must be the directory that owns the artifact. Adopt one pattern across a course and say it once in the root index: harness writes are sandboxed to the lab's own folder, and only labs that consume the repo's existing harness open at the root. Add a restart instruction wherever `.claude/settings.json` changes, because hook configuration is read at startup and an unrestarted session runs the old policy while looking correct.

## Instructions handed to running background work go stale

**Pattern (2026-07-24):** A workflow unit was launched with the premise "`.claude/commands/` does not exist, so rewrite Step 4 around the global authoring skill". Minutes later the user asked me to restore those command files, which invalidated the premise while six agents were mid-flight. The unit finished and rewrote the guide around the wrong target, and the result had to be undone by hand afterwards.

**Rule for the future:** When a user request invalidates a premise already given to running background work, say so in the same turn and name the specific file that will need correcting when it lands. Stopping a workflow three minutes in throws away real work, so the cheaper path is usually to let it finish and apply a scoped correction, but only if the debt is recorded the moment it is incurred rather than rediscovered later.

## Compress a guide by counting model round-trips, not words

**Pattern (2026-07-24):** Two labs were shortened without losing teaching. One went from 1h 30m to 1h by merging three tool-writing steps into two and three verification steps into one: 8 steps to 5, and 16 model round-trips to 10. Another went from 1h 30m to 1h 15m by merging two MCP registration tasks that were the same mechanism performed twice, each costing its own `/exit` restart cycle.

**Rule for the future:** In a prompt-driven guide the clock is set by round-trips and session restarts, not by word count. Look for steps that repeat a mechanism already taught: the first occurrence is teaching, the rest are typing. Merging them is usually better pedagogy too, because putting an HTTP MCP entry and a stdio MCP entry in one file side by side teaches the contrast that two tasks a hundred lines apart cannot.

## Compute counts, do not add them mentally

**Mistake (2026-07-24):** I reported "25 lab guides" several times across the session. The real figure was 27 `lab-*.md` files plus 2 sub-lab readmes, 29 in total. The error came from adding a per-module inventory by hand and getting 14 instead of 16 for the first half.

**Rule for the future:** Any count that goes into a deliverable or a status report comes from a command, not from mental arithmetic over a list I just read. The same applies to time totals in a table: sum them with a script and state the computed figure, because a table of thirteen durations is exactly the kind of thing that looks right and is off by fifteen minutes.

## Do not assert a distinction that no longer exists

**Pattern (2026-07-28):** A topic page opened with "what separates them is packaging and how deliberately you control invocation", then spent a paragraph on an invocation "axis" whose own text admitted both forms behave identically (`description` matching and `disable-model-invocation` work the same in `.claude/skills/` and `.claude/commands/`). The user pushed back three times, correctly: the paragraph asserted a difference and then described a non-difference. The fix was to drop the second axis and state the reader-facing instruction instead: do not pick the folder in order to control triggering.

**Rule for the future:** Before writing a comparison, check that every named axis actually separates the two things. When a formerly-real difference has been merged away, that merge is the teaching point: say "this looks like a second difference and is not one, here is what to use instead" rather than salvaging the framing. A comparison table is the tell, since a row whose two cells say "the same" is a row that belongs in prose as a non-difference.

## Course pages that document a live product decay silently

**Pattern (2026-07-28):** Three topic READMEs in module 03 cited `code.claude.com/docs/en/skills` and had drifted from it. `skill-creator` was described as built into Claude.ai with a 15-to-30-minute authoring flow, while the current docs make it a marketplace plugin (`/plugin install skill-creator@claude-plugins-official`) whose documented purpose is an eval loop with `evals.json`, `grading.json`, and `benchmark.json`. A publishing page went further and claimed it "does not produce quantitative evaluation results", the exact opposite. The description cap was documented as 1024 characters against a current 1,536, and two rules (reserved `claude`/`anthropic` name prefixes, forbidden angle brackets) appear nowhere on the cited page. Separately, `03-composite` told learners to reference bundled scripts by relative path, which fails because commands run from the project root, not the skill folder.

**Rule for the future:** A page that cites a documentation URL is making a checkable claim, so fetch that URL and diff before shipping edits to it. Treat three things as defects rather than staleness: a stated numeric limit, a described install path, and an inverted capability claim. When the page teaches a mechanic (a path, a substitution, an invocation), run it once instead of reasoning about it.

## Demo harness artifacts belong in the repository harness, not the demo folder

**Pattern (2026-07-28):** A new topic shipped its two demo skills inside `04-advanced/order-api-solution/.claude/skills/`, and an older topic had the same shape in `02-creating/skill-from-conversation-solution/.claude/`, complete with a readme paragraph justifying it as "self-contained". The user corrected this twice. Moving them to the repo's `.claude/skills/` changed the working directory the injected commands run from, which broke every relative path in them.

**Rule for the future:** Finished demo skills live in the repo's `.claude/skills/` so `/name` works from the repo root like any other skill; only the artifacts a learner's run produces stay in the solution folder. A skill hosted at the root that targets a demo folder must anchor every path with `${CLAUDE_PROJECT_DIR}`, which does get substituted inside `` !`command` `` injection blocks. That was verified by running the skill, not assumed.

## A headless self-report is not evidence about the CLI

**Mistake (2026-07-28):** To check whether `/skills`, `/plugin`, and `/reload-plugins` exist, I asked `claude -p` to list which of them are available. It reported `/skills` and `/reload-plugins` as MISSING, and I passed that uncertainty to the user as something they should verify by hand. Both exist. The `-p` path does not expose interactive menu commands, so the model was answering about its own session rather than about the installed build.

**Rule for the future:** Verify a tool's surface against an artifact that cannot be polite about it: grep the installed binary or package for the literal command string, and include a control string that must return zero. A model asked "does X exist" reports what it can see from where it is standing, which is a different question. The same applies to the docs, where a commands reference page can omit a command that another page of the same site instructs you to type.

## When a lint rule contradicts itself, fix the rule file

**Pattern (2026-07-28):** The repo brand-voice rules banned repeating one generic slash-command set across modules, while its approved-sets table gave a single coarse row for the whole Skills module. Following the table would have put an identical three-command set on all six topic pages, violating the rule's own paragraph. I shipped distinct per-topic sets and flagged the conflict; the durable fix was to replace the coarse row with one row per topic.

**Rule for the future:** When a repo's own quality rule cannot be satisfied as written, edit the rule source rather than quietly deviating from it or complying against the intent. A rules file with per-module granularity will hit this whenever a module grows past a few topics, so record the resolved sets there so the next author inherits the decision instead of relitigating it.

## "Is X mentioned here?" is a request to verify X, not to confirm it exists

**Pattern (2026-07-28):** The user asked whether the MCP intro should mention the MCP Inspector. It already had a dedicated section, so the cheap answer was "already covered at line 199". Reading that section against the Inspector's current docs found two defects instead: the config example used `"type": "streamable-http"`, which is not a valid value (`stdio`, `http`, `sse` are), and the closing line credited `--server` with switching targets in a browser UI that ignores the flag, since it "selects only under `--cli`". A learner copying that block gets a rejected config.

**Rule for the future:** When someone asks whether a topic is covered, they are pointing at it for a reason. Open the section and re-verify its claims before answering, because the likely reasons for the question are that it is buried, thin, or wrong, and only one of those is answered by "it is already there". Anything copy-pasteable in the section (a config value, a flag, a command) gets checked against the source, not eyeballed.

## A new topic silently makes its neighbours redundant

**Pattern (2026-07-28):** Adding `04-advanced` and rewriting `06-evolution` moved two subjects out of `02-creating`, but nothing removed them from it. The creating page kept a full dynamic-context-injection section and the entire `skill-creator` eval loop, so three of six topics in the module taught the same material, and the module TOC still advertised the creating page as covering "the skill-creator interactive guide". The user caught it as "this contains lots of information that is covered in other topics".

**Rule for the future:** After adding or rewriting a topic in a numbered module, re-read its neighbours in the same pass and delete what the new topic now owns, replacing it with a one-line pointer. State the split explicitly near the top of each page so the boundary is visible to the next author. Then re-check the module TOC row and the topic's own command table, because both describe content that may have just moved out.

## A generated binary can pass every check and still refuse to open

**Pattern (2026-07-28):** `slides/modules/module_01.pptx` would not open in PowerPoint, yet python-pptx loaded it, `zipfile.testzip()` found no bad entry, every part declared in `[Content_Types].xml` existed, all relationship targets resolved, and a hand-written scan for schema-order and duplicate-id violations came back clean. The actual defect was one attribute: `render_table` computed `table_y` as a Python float, so the file carried `<a:off y="2400300.0"/>`, and `ST_Coordinate` is integers only. Every library in the chain was happy to read a value that the real consumer rejects outright.

**Rule for the future:** For a generated binary format, the acceptance test is opening the artifact in the application that consumes it, not a round-trip through the library that wrote it. On Windows that is cheap: drive PowerPoint or Excel through COM in a loop and assert every file opens. Isolate a corrupting generator by emitting one artifact per input unit (here, one deck per slide) and opening each, which named the failing renderer in a single pass instead of by inspection.

## A renderer that reads fields with .get() loses content in silence

**Pattern (2026-07-28):** Four separate content losses shipped without a single error. `caption` is read from the YAML on every diagram but only rendered for `flow` and `architecture`, so it vanished on `comparison` and `decision`; `caption` was likewise dropped by `render_terminal` on all eight terminal slides in the course. A subagent invented an `items_note` field that no renderer reads. A `comparison` that sets `variant` on one side only does not stay neutral, it paints the other side red, which inverted the meaning of a slide whose own source called that boundary "the useful part".

**Rule for the future:** When a template layer reads a data dict with `.get()`, the build can never fail on a typo or a misplaced field, so write a linter that whitelists the legal fields per type and run it before the build. Check the traps a schema cannot express in the same pass: a field that is read but conditionally ignored, an enum value accepted but unstyled, and a paired setting that changes meaning when only one half is present. `slides/pptx/build/lint_content.py` is that gate here.

## An estimating validator is not proof that the output looks right

**Pattern (2026-07-28):** `validate.py` reported `Total findings: 0` on decks that were visibly broken. A terminal window rendered its last line below the frame, because the height estimate used `points * spacing` while PowerPoint applies percentage line spacing to the font's line box, roughly 1.2x the point size. Worse, every `flow` step printed the literal text `{'label': 'Write 3 to 5 prompts', 'desc': ...}` on the slide, since `render_flow` only ever accepted plain strings. Both were found by exporting the deck to PNG and looking at it.

**Rule for the future:** A validator that estimates geometry can only catch what it models, and it models neither a shape drawn outside its container nor a Python repr rendered as prose. Export generated visual output to images and read a sample of every distinct layout type before declaring the artifact done. Choose the sample by layout, not by position, because one unchecked type is one wholly broken family of slides.

## A wrong shared contract is amplified by every agent in the fan-out

**Pattern (2026-07-28):** Fixing the slide schema on the main thread before dispatching 29 drafting agents was the right shape, and the contract still carried a defect: it specified `flow` steps as `{label, desc}` objects, inferred from neighbouring diagram types rather than read off `render_flow`, which takes strings. All four modules came back with unusable flow steps, and the fix landed in the renderer only because a screenshot caught the raw dicts on a slide. The adversarial critics did not catch it either, since they were checking drafts against the same wrong contract.

**Rule for the future:** The coordinator writing the contract before fan-out is necessary but not sufficient; every field in it must be read off the consuming code, not inferred from a sibling field or an adjacent example. Verify the contract against the consumer once, before it is copied into N prompts, because a contract error is the one class of mistake that per-item review cannot see. Where the consumer is permissive about shape, prefer widening it to accept both forms over rewriting the data.

## The skill that documented my trap was one I never opened

**Pattern (2026-07-29):** Verifying an orchestration script that shells out to `claude`, I stubbed the CLI by dropping an extensionless `claude` into a folder prepended to `PATH` as a Windows-style path (`C:/Users/.../stub`). Git Bash ignored it, the real CLI ran inside a backgrounded parallel loop, and two live billed sessions executed before the log revealed it. `create-class/references/verify-by-execution.md` already carried this verbatim, including the fix (`cygpath -u`) and the assertion that catches it (`which claude`). `CLAUDE.md` says to check `.claude/skills` before implementing; I went straight to writing the harness because stubbing a binary felt too small to warrant a lookup.

**Rule for the future:** Consult the owning skill before building any verification harness, not only before building the deliverable. The judgement "this is too small to need the skill" is exactly the case the skill exists to correct, because a documented trap is invisible precisely when the technique looks trivial. When a stub must shadow a real binary, prefer `export -f <name>` over `PATH`: a shell function cannot be silently outranked by path resolution, so it needs no `which` assertion. If `PATH` is used anyway, assert `which <name>` resolves to the stub before running anything that can spend money.

## A demo's home is the topic whose files it reads

**Pattern (2026-07-29):** `demo-worktree-orchestration.md` looked like an orphan and was not one: it held a row in the module TOC and an entry in the dashboard. What was actually wrong sat below that surface. It had no starter of its own, drew its Setup from a *lab* sandbox two directories away, told the learner to read a script living in a different topic folder, and pointed its "completed reference" at a sibling demo's solution, which is why nothing in that solution matched what the guide produces. Its material was orchestration, not worktree mechanics.

**Rule for the future:** Test a guide's placement by what it reads, not by whether something links to it. A guide whose Setup, reference implementation, or solution pointer resolves outside its own topic folder is misfiled, and the topic that owns those files is its home. Being indexed proves only that the TOC was maintained; three cross-topic references and a borrowed solution pointer prove the guide never ran where it sits.

## Only the failure path found the defect

**Pattern (2026-07-29):** The orchestration script passed its success path on the first run: two worktrees created, agents launched in parallel, per-PID exit codes collected, both branches merged, everything cleaned up, exit 0. Re-running with one agent forced to exit non-zero showed it abandoning both worktrees on disk, contradicting the guide's own Step 1, which expects cleanup even when the run aborts. The script had been written from the guide's numbered design, where cleanup is step 6 and therefore unreachable once step 4 exits.

**Rule for the future:** A script with an abort path is verified only when the abort path has been run. Design specs written as numbered phases invite exactly this bug, since teardown lands last and every early exit skips it; read such a design for what each `exit` leaves behind before implementing it. Forcing the failure costs one extra run and is the only thing that distinguishes a script that aborts cleanly from one that aborts and leaks.

## The flag named for allowing was not the flag that restricts

**Pattern (2026-07-29):** `demos/05-cli/01-intro/readme.md` taught that limiting a run to `--allowed-tools "Read,Glob,Grep"` "prevents any write operation no matter what the prompt says." Running it created the file. `--allowed-tools` is an allow list that waives permission prompts and removes nothing; the restrictive flag is `--tools`, which the module never mentioned, and the CLI reference says so in one line under the very flag the readme cited. Two further runs showed `--disallowed-tools "Write,Edit"` blocking the tool while the model recreated the file through PowerShell. Three topics and both `lint-with-claude.sh` copies had been built on the inverted claim.

**Rule for the future:** A claim that something is *prevented* is the one class of course content that must be executed, because it fails open and silently: the wrongly-scoped run still returns a correct-looking answer and nothing errors. Test an enforcement claim by asking the agent to do the forbidden thing and checking the filesystem, never by reading the flag's name or trusting that a plausible name implies a direction. When the docs describe a flag, read the sentence that says what it is *not* for; the answer here was one clause pointing at a different flag.

## Correcting the scope changed the turn budget

**Pattern (2026-07-29):** Swapping `--allowed-tools` for `--tools "Read,Glob,Grep"` in the CI-gate scripts was the correct fix and it broke the demo. The old flag had quietly left Bash available, so the audit read the project in a few shell calls; the genuinely read-only run spends a turn per file it opens, blew through `--max-turns 5`, and exited 2 (indeterminate) instead of gating the build. Only re-running the script surfaced it, and the readme's "a code audit rarely needs more than five turns" turned out to have been true only because the scoping never worked.

**Rule for the future:** A permission change is also a performance change, because the turn count is a function of the tool set, not of the task. After changing any scoping flag, re-run every artifact that consumes it rather than assuming a correctness fix is behaviour-neutral. Treat a surrounding numeric budget (`--max-turns`, timeouts, retries) as calibrated against the old tool set and therefore stale, and recalibrate it in the same pass.

## The ceremony I preserved was a constraint nobody had stated

**Pattern (2026-07-29):** `demo-worktrees.md` opened by sending the learner to a lab in another module for its project. I fixed that by building a self-contained starter, then kept the guide's original ceremony and made it worse: copy the folder to `/tmp`, `git init`, make a first commit, all to protect the course repository's history from two merge commits. The user's answer was flat: "it is a claude class not about git init", then "we want to start in the starter". The repository was a git repository the whole time, with commits, a writable parent for worktrees, and merge commits that are trivially discardable in a learner's own clone.

**Rule for the future:** When a guide's setup exists to avoid a consequence, name the consequence in one sentence and let the reader own it, rather than engineering a sandbox around it. Preserving an existing workaround while fixing the thing next to it is how an invented requirement survives a rewrite: the ceremony was never in the brief, and inheriting it counts as inventing it. Ask what the learner is here to practise; in a class about an agent harness, `git init` is not it.

## A starter that ships the finished artifact makes its own first step a no-op

**Pattern (2026-07-29):** `worktrees-demo/worktree-workflow.sh` was byte-identical to `worktrees-demo-solution/worktree-workflow.sh`, and `lint-with-claude/lint-with-claude.sh` was byte-identical to its solution, while Part A of each guide asks the learner to write that script from a prompt. The learner opens the starter and the answer is already there. The reverse case sat two folders away and looked identical: `parallel-worktrees/` also ships a finished script, but its sibling guide sends the reader in to *read* it as a reference, so removing it would break that demo.

**Rule for the future:** Audit a starter by diffing it against its solution, then split the difference by verb: stub what the guide asks the learner to *build*, keep what the guide asks them to *run* or *read*. A file that both guides in a topic disagree about is decided by the consuming guide, never by the producing one. The same rule extends across topics: a topic's starter holds everything its own demos consume, even when an earlier topic is where that artifact was built.

## A worktree of a course repository does not put the demo at its root

**Pattern (2026-07-29):** Three orchestration scripts in module 05 created a worktree and ran `cd "$WORKTREE"` before launching an agent told to edit `src/slugify.ts`. That works when the repository *is* the project, and this repository is a course: the worktree root holds `demos/`, `labs/` and `slides/`, so every agent would have started in a folder with no `src/` in it. The scripts had been written against `git rev-parse --show-toplevel` alone, which is the correct answer to a question nobody was asking.

**Rule for the future:** Inside a repository that contains many projects, a script that spawns worktrees needs two coordinates, not one: `--show-toplevel` for the repository and `--show-prefix` for the folder it was launched from, then `cd "$WORKTREE/$PREFIX"`. Verify it by creating one worktree and listing that path, which takes seconds and is the only check that distinguishes the two cases. Prefer `--show-prefix` over a hardcoded relative path so the same script serves the starter and the solution unchanged.

## Placement is settled by prerequisite order, not by the artifact a lab produces

**Pattern (2026-07-29):** Module 03 (Skills) shipped a core lab that authored a skill by mining a Python MCP server, and MCP is module 04. It had been filed under Skills because its output is a `SKILL.md`. The same error had leaked into naming one module over: a module 06 planning demo was called "Decompose a Spec into Sub-Agent Packages" and its prompt asked for "sub-agent packages", although nothing is delegated in it and subagents arrive in module 07.

**Rule for the future:** A guide belongs to the module whose already-covered concepts it *requires*, not to the module its output resembles. Check the vocabulary in the same pass, including the filename: a title that borrows a term from a later module teaches the term before the module does, and renaming the file is part of the fix. When a lab moves out and leaves its module without a core lab, the replacement is part of the move, not a follow-up.

## The framework's command surface had drifted from every page describing it

**Pattern (2026-07-29):** The Spec Kit topic documented `/speckit.constitution` and friends as slash commands, and the setup script's live run printed `/speckit-constitution` and installed ten entries into `.claude/skills/`. Hyphens, not dots, and skills, not commands. BMAD was the same shape: 46 skills, with the roles the guide called "the PM agent" actually invocable as `bmad-agent-pm`. Both pages read as plausible and both were wrong in a way no proofread catches.

**Rule for the future:** For any third-party tool the course drives, install it and list what it actually registered before writing the commands into a page, and re-check on every revisit, because a CLI that installs from `git+https` moves between classes. Prefer capturing the surface from the tool's own output (`--help`, the install summary, the on-disk `.claude/skills/` listing) over the project README, which lags its own CLI.

## Ten rounds of corrections rebuilt a checklist that was already written down

**Pattern (2026-07-29):** The user corrected the same page repeatedly: reference a lab from another module, `mkdir` a project in the Setup, copy the starter to `/tmp` and `git init` it, nest a second project level inside the starter, ship the finished script in the starter. Each correction was absorbed and applied one at a time. At the end of the session, `create-class/references/create-guide.md` turned out to hold all of it already: a "Setup is one command" section, a defect table whose rows are literally `mkdir x && cd x && claude` and `cp -r ../<other-topic>/...`, "One self-contained starter per topic", and "The starter must not contain the deliverable" with `diff -rq <starter> <starter>-solution` as the detection command. This is the second time in two days that the owning skill documented the exact trap that was walked into (see "The skill that documented my trap was one I never opened").

**Rule for the future:** Before touching any demo or lab guide, read `create-class/references/create-guide.md` and run its `diff -rq` check on the topic in question; treat it as an entry gate, not as reference material to consult when stuck. The first correction from the user on a guide is the signal that the owning skill was not opened, so stop and read it then rather than continuing to patch. A rule the user has to teach through repeated correction is almost always a rule that already exists in writing, and the cost of checking is one file read against roughly ten round trips.

## Aligning an agent means changing what it can do, not fencing it off

**Pattern (2026-07-29):** Module 13 was rebuilt around deploying to an Ubuntu host over SSH, and the user said the harness agent would also have to be aligned. I kept `github-devops-agent` Azure-scoped and added a Scope Boundary section instructing it to decline SSH work, because the topic page I had just written used it as the cloud-managed contrast case. The user repeated the instruction, this time leaving no room: "i asked you to rescope that agent to what we need ... ssh based deployment and github". The rescope took one file: drop twelve `azure-deploy` MCP tools, add the `permissions` allowlist it never had, and replace the Bicep and Workload Identity sections with host access, rollout and the edge.

**Rule for the future:** When the user says align or rescope an artifact to new work, change its capability. A page that describes the old scope is downstream of the artifact, so it gets updated in the same pass; it is never the reason to preserve the old scope. Fencing an artifact off from the work it is now needed for is the exact opposite of aligning it, and dressing that up as a "scope boundary" makes the gap harder to see, not easier.

## A capability nobody can reach is half a delivery

**Pattern (2026-07-29):** The user pasted an `ssh-mcp` server block with "add this mcp to .mcp.json". I added it verbatim, flagged the tracked-password exposure, and stopped, minutes after rescoping the deployment agent to reach hosts over SSH. The user's next message was "why didnt you give the agent the ssl mcp". The wiring was two lines: `mcp__ssh-mcp__*` in the agent's `tools`, and no duplicated `mcpServers` block, because the project-scope definition already carries the credentials and copying it would have put the password in a second tracked file.

**Rule for the future:** After adding a capability (an MCP server, a script, a credential, a tool), ask which existing artifact exists to consume it and wire it in the same pass. This does not conflict with the rule against inventing requirements: that rule forbids adding constraints the user did not state, not leaving a capability the user did state unreachable. The test is whether the thing works end to end for the reason it was asked for.

## Totals belong in the table, as a row

**Pattern (2026-07-29):** Asked to re-estimate a timing table and then to add the remaining modules, I split one table into "Modules 1 to 6" and "Modules 7 to 13" with a subtotal each plus a third summary table. The correction was four words long: "this is one table". Later, replacing the labs index totals, I wrote them as two bold prose paragraphs and got "you messed this up ... i want totals for techings, labs and overall total nicely presented as a row".

**Rule for the future:** A table's totals go in the table as a `**Total**` row, and a second set of figures gets a second row rather than a paragraph. Extending a table means adding rows to it, never reorganising it into sections with headings the user did not ask for. When two totals legitimately differ, put both in rows and reconcile them in one sentence underneath, because a reader who finds two numbers and no explanation reads it as an error.

## Two agents cannot agree on a file layout while running in parallel

**Pattern (2026-07-29):** In one workflow stage, one agent wrote the Compose and TLS guide while another created the starter it walks through. The guide came out written against `web-app/`, `stack/docker-compose.yml` and services named `web` and `edge`; the starter shipped `app/`, root-level stubs and services named `caddy` and `app`. Every step in the guide referenced a file the learner does not have, and only the verify stage caught it. My global rules already say the coordinator writes the shared interface before fanning out, and I had applied that to the module's table of contents while treating the starter's layout as an implementation detail.

**Rule for the future:** A file layout is an interface: paths, service names, container names and published ports all count. Write it down before fan-out, or sequence the consumer strictly after the producer, because two agents inferring the same layout independently is an integration failure no build catches. The tell that this was mishandled is a guide whose commands are internally consistent and match nothing on disk.

## A workflow's own report is a claim, not evidence

**Pattern (2026-07-29):** A thirteen-agent run returned an `authored` array listing all eight content jobs, and nine agents had actually died on API 500 and 529. My pipeline stage mapped each result into `{label, report}`, so a `null` from a dead agent still produced a labelled entry. Separately, three verifiers ran concurrently with write access to the same tree: one rewrote the broken guide against the real starter, another read it mid-rewrite and reported the pre-rewrite mismatch as an unfixed blocker. Only opening the file settled which of the two reports was true.

**Rule for the future:** Filter on the payload, not the label, since `agent()` resolves `null` on terminal failure, and reconcile any claim of authorship against the files on disk before reporting it. Do not let parallel verifiers that also fix things overlap in files: give each a disjoint set, or split find from fix. Treat every surviving "blocker" from a concurrent verify stage as a claim to check, because the cheapest explanation is that it read a file another agent was still writing.

## Every defect my checker reported was a defect in my checker

**Pattern (2026-07-30):** Three verification scripts over 51 generated guides reported 20 defects between them, and all 20 were bugs in the scripts. A naive backtick toggle read a 4-backtick ````markdown` fence wrapping a 3-backtick ```text` fence as two unbalanced fences and flagged 8 files for "no language". An elision splitter matching `\n...\n` missed indented `      ...` and flagged 8 snippets as fabricated, the single worst defect class in the run. A `(\d+)\s*min` regex could not see `1.5 min` and flagged 4 files as over budget. In one case the script reported `guides=0` alongside eight all-clear counters, because a `cd` in an earlier command had moved the shell out of the tree.

**Rule for the future:** A verification script is code written in one pass and trusted absolutely, which is the worst combination in the repository. Before reporting any defect it finds, reproduce one instance by hand; if the hand check disagrees, the script is wrong. Assert the input count in the output (`guides=51`) so a run that matched nothing cannot look identical to a run that passed, and make nesting, indentation and non-integer numbers explicit test cases, because those three are where every one of these bugs lived.

## The estimate was the deliverable before any file was

**Pattern (2026-07-30):** Asked to cut a course from 4.3 days to 3.75 by presenting demos instead of running them, I began reading guides and was two steps from writing files when the instruction arrived: "befor starting to change files present you expected timing info", then "break it down to demo level", then "create an artifact". The user had already supplied the calibration in the same breath, "i think module 1 1:15 is possible that way", and a costing model fitted to that anchor reproduced 1h 15m exactly and then derived all 51 other numbers from the same three rules.

**Rule for the future:** When the deliverable is downstream of a numeric model (a schedule, a budget, a headcount), the model is what needs approval and the files are only its consequence. Present it at the granularity of the thing being changed, one row per unit, before touching anything. Where the user states a target figure for one unit, fit the model to that figure rather than deriving an independent one and comparing: their number encodes a judgement about the room that the inputs do not contain.

## A path inside a code fence is not navigable

**Pattern (2026-07-30):** Presenter guides quoted prompts verbatim, so a beat teaching `@Controllers/UsersController.cs @Models/PaginatedResponse.cs` displayed both paths and made neither clickable, because Markdown does not render links inside a fence and the snippets could not be altered. The second half of the same correction was worse: 104 of 236 beats opened with a bare link to the source guide they present, identical in every beat of the file and already named in the frontmatter. It read as navigation and was provenance.

**Rule for the future:** Any file path a reader is told about must be reachable outside the fence, on its own line, with the three cases separated: real files get a relative link, files the exercise creates get inline code plus which step writes them, and paths outside the repository get inline code only. A link that repeats identically in every section navigates nowhere; anchor it to the specific heading and require every section to link at least one thing other than its own parent document. Resolve every `#anchor` against the target file's real headings, since a file-existence check passes an anchor that scrolls nowhere.

## Fixing the code falsified the page that documented the bug

**Pattern (2026-07-30):** Two demo starters shipped controllers already returning `PaginatedResponse<T>`, making each demo's central edit a no-op, and the presenter guides had handled that honestly with an "If the room asks" row explaining that Step 5 changes very little. Correcting the starters turned both of those rows into false statements. The documentation of a defect is coupled to the defect, and nothing in a build or a link check notices when one half moves.

**Rule for the future:** Before fixing a defect, grep for content that describes it, and fix both halves in the same pass. Prefer rewriting the explanation to ask what is now true over deleting it, because the row existed for a reason the room will still raise. This is the mirror of the rule about wiring a new capability in: a change is not finished while some page still describes the old world.

## A lesson already written down did not stop the defect shipping twice more

**Pattern (2026-07-30):** "A starter that ships the finished artifact makes its own first step a no-op" was recorded the previous day with a diff-based audit as its rule. One day later, `constitution-api` and `model-routing-api` were both found shipping fully paginated controllers while their guides instruct the learner to add pagination and their Step 1 Finding claims neither controller returns the type. Neither topic has a `-solution` folder, so the prescribed `diff -rq <starter> <starter>-solution` audit could not have caught either one. What did catch them was authoring a second artifact from the same sources, which forced a reading of every starter against its own guide.

**Rule for the future:** A rule expressed as a diff between two folders cannot see a starter whose contradiction is with its guide rather than with a solution. Check the guide's own claims against the starter: every Finding that asserts what the code does, and every Recipe whose deliverable already exists, is a mechanical check that needs no solution folder. When a recorded lesson recurs, the rule was too narrow rather than ignored, so widen the check instead of restating the principle.

## A module about the shell cannot be written shell-agnostically

**Pattern (2026-07-30):** Module 5 shipped eleven `.sh` scripts and every guide command in `bash`, on a course whose author and most learners are on Windows. The authoring rule I was working from says to prefer commands that are byte-identical in both shells and to reach for dual blocks only where the shell's own commands differ, which is correct for a module that merely uses a shell and useless for one whose subject is job control, exit codes and stdin. Four of the translations turned out to carry the actual teaching: a PowerShell job reports `Completed` even when the command inside it exited non-zero, so the orchestrator has to emit `$LASTEXITCODE` as the job's last statement; `-match` is case-insensitive, so a `grep -q LINT_FAIL` translated naively silently loosens a sentinel-token gate; `ConvertFrom-Json` deletes the `jq` prerequisite the hook demo states in its own Setup; and `Parser::ParseFile` is the `bash -n` equivalent while `chmod +x` has no counterpart at all.

**Rule for the future:** Where a module teaches the shell rather than merely using it, ship every script twice and print both blocks, because the differences are the lesson and hiding them costs the Windows half of the room the module. Where a command is plain `git` or plain `claude`, keep one block; the test is whether the shell's own machinery appears, not whether the file has a `.sh` name. Two authoring traps came with it: a starter stub must be duplicated as an empty `.ps1` or the "fill in this file" step has no file on Windows, and a literal `|` inside a Markdown table cell breaks the table even inside backticks, so a translation table describes `-split` and `IFS` in words rather than showing them.

## Adding a variant to a timed guide is not the same as adding it to a reference guide

**Pattern (2026-07-30):** Adding PowerShell to module 5 meant touching five demo guides and five presenter guides. The demo guides absorbed dual blocks cleanly, since a learner reads one block and skips the other. Applying the same treatment to the presenter guides would have doubled the length of documents whose entire contract is four beats inside a four-minute budget, to teach a presenter who has already chosen a shell and will project exactly one of them.

**Rule for the future:** A presenter guide gets one paragraph after its Assets table naming the counterpart file and the specific beats where the variant changes shape, never a second copy of every quoted block. The budget in the frontmatter is a real constraint: content that cannot be delivered inside it is not an addition to the guide but a replacement of it. The reduced treatment has one hard floor, found by auditing the first pass against the repo's Windows-fatal list: the paragraph must name every form in the quoted blocks that fails outright on the other platform, because a presenter types those live off the projected slide. My first pass named the interesting differences (`-cmatch`, `Start-Job`) and missed the fatal ones (`$?` printing `True`, `< /dev/null` as a parse error), which is exactly backwards.

## The filesystem workaround I was about to teach had a first-class flag

**Pattern (2026-07-30):** A demo needed a genuine no-skill control run, and the guide told the learner to `mv .claude/skills/code-reviewer /tmp/` and put it back afterwards. The same ceremony had also leaked into a solution artifact and a slide. `claude --disallowedTools Skill` removes the Skill tool for one session and needs nothing on disk to move. The same shape repeated three more times: `git stash push -- <path>` held two versions of one tracked file instead of a second copy, `git diff <path>` replaced keeping a pristine copy to diff against, and `git ls-files` replaced `cp -r` when duplicating a project (83 MB of build output versus 129 KB of tracked source).

**Rule for the future:** Before writing a move, copy, or backup into a guide, ask what the tool itself offers, then verify the answer rather than assuming it. A one-line headless run (`claude -p "..." --disallowedTools Skill`) settled it in seconds and made the guide honest. When the workaround is already published, grep for it: it had spread to a solution file and a slide deck that no link check or build would ever flag.

## A cleanup command that removes nothing looks exactly like one that worked

**Pattern (2026-07-30):** I instructed an agent to end a demo with `git clean -fd` over four paths. The agent checked `git check-ignore` and found all four are gitignored, which is precisely why plain `git clean -fd` skips them; it needs `-fdx`. My command would have run, printed nothing, exited zero, and left every file in place. The mirror image appeared in my own verification: an em-dash count of 134 in HEAD against 521 in the working tree looked like a large regression, but the two numbers came from different file sets and one counted matching lines while the other counted occurrences. Measured like for like, both were 152.

**Rule for the future:** A command whose success output is silence needs its precondition checked, not its exit code: run `git check-ignore` before writing any `git clean` into a guide. For any before/after number, produce both sides with the identical command over the identical path (`git grep -oh X HEAD -- p` against `git grep -oh X -- p`) before believing a delta, because a comparison across two different measurements is not a measurement.

## Every subagent reported my own work as a stranger's

**Pattern (2026-07-30):** Nine subagents ran over one checkout. Eight of them closed by warning me about "a large set of uncommitted changes from another session", listing a folder rename and ~140 modified files that were mine, made minutes earlier in this same session. Exactly one foreign thing was in the tree, a batch of `.ps1` files under one module. An agent reads `git status` and sees state with no author attached; it cannot tell the coordinator's in-flight work from a third party's, so it defaults to the cautious reading and is wrong almost every time.

**Rule for the future:** Tell each agent what is already in the working tree and whose it is, naming the one folder that genuinely belongs to someone else, so its caution lands where it matters instead of on my own edits. Never relay an agent's attribution of working-tree state to the user without checking it against what I did: repeating "another session changed this" about my own work turns a status report into misinformation.

## Copying a folder to a new topic carried links that resolve to nothing

**Pattern (2026-07-30):** Removing cross-topic borrowing meant copying a finished solution folder from topic 06 into topic 07. Its readme opened with a link to `../demo-fan-out-orchestration.md`, correct in 06 and a dead path in 07, because the sibling it names does not exist there. Nothing catches this: the file is present, the markdown is well formed, no build reads it. A resolver over all 132 relative links in the module found it immediately.

**Rule for the future:** A copied folder inherits its author's location. After duplicating one anywhere, resolve every relative link and `#anchor` from the new path before calling it done, and treat provenance sentences ("this is a copy of X") as content to retarget rather than history to preserve.

## Fixing where the session starts broke what the session can reach

**Pattern (2026-07-30):** Giving three topics their own project starters looked complete, and the guides passed a "no borrowed paths" grep. But two of them are fan-out demos driving a .NET service and an Angular client together, and `cd`-ing into the .NET starter put the session where the Angular half was unreachable. The grep was green because every path was topic-local; the demo was still broken. The fix was to root the session at the topic folder that holds both starters, which then contradicted a module readme sentence I had written an hour earlier.

**Rule for the future:** When a demo drives more than one project, the working directory is the smallest folder containing all of them, not the first starter in the list. After changing where a session starts, re-check every path in the guide against the new working directory, since paths made relative for the old one are now silently wrong, and re-read any page describing the layout: a structural change falsifies its own documentation faster than anything else in the repo.

## I swept 51 files against a spec that was missing its most important element

**Pattern (2026-07-31):** Asked to drop the Assets table from presenter guides and add a teaching intro per beat, I updated the authoring spec, wrote the intro rule, fanned out eight agents, and verified all 51 files clean. The result was still wrong. A presenter guide is a goal, then actions, then result, and the required structure I was enforcing had no result element at all: every beat quoted the prompt and the command and then a prose sentence saying what a good outcome looks like, so the run's actual output never appeared anywhere. The demo guide underneath it did the same thing ("a good outcome is exit code 1 with LINT_FAIL in the output"), which is a description of a result standing in for one. I had treated a document-shape request as a formatting request and never asked what the document is for.

**Rule for the future:** Before a bulk edit across a document class, write down in one sentence what that document is for, and check the required structure delivers it end to end. A sweep multiplies a spec defect by the file count, and the verification I built confirmed conformance to the defective spec with total confidence. When a guide's own prose says what the result would be, that is the tell: a result is evidence (real output, the artifact on disk, a diff against the starter), never a prediction, and `<starter>-solution/` is the record of what the agentic run actually produced.

## My verifier's key lookup never matched, so every fence check silently passed

**Pattern (2026-07-31):** I hashed 333 code fences before a 51-file sweep so any agent that altered a verbatim snippet would be caught. The baseline JSON stored Windows paths with backslashes; the checker normalised its lookup keys to forward slashes and called `base.get(key, [])`. Every lookup missed, every comparison ran against an empty list, and the script printed `STRUCTURE: ALL CLEAN` across all 51 files. I only noticed because I had just deliberately shortened one fence and the run failed to flag it. Once fixed, it correctly found 5 changed fences. Separately in the same session, a `cd` in an earlier Bash call persisted and made the same script report `checked files: 0` alongside `ALL CLEAN`; only the printed input count gave that away.

**Rule for the future:** A lookup that misses must fail loudly, never default to a permissive empty value. Assert the baseline is non-empty, assert each file has a baseline entry, and treat a missing key as a defect rather than a pass. Then prove the checker can fail: break one input on purpose and confirm it is reported, because a verifier that has never failed is indistinguishable from one that cannot fail, which is the same lesson as the CI gate the course itself teaches.

## Adding what was asked for, without subtracting, inflated 51 files by half

**Pattern (2026-07-31):** Asked to add a 2 to 3 sentence teaching intro to every beat, I did exactly that across 232 beats and verified it clean. Prose went from 29,911 words to 44,637, a 49% increase, and the longest guides reached 1,300 words for a five-minute demo read off a second monitor. Each individual addition was requested and defensible; nobody was asked to pay for them. The later instruction "do not bloat it with text" was not a new requirement, it was the constraint I should have inferred from what the document is for.

**Rule for the future:** When adding a required element to every unit of a document set, decide in the same pass what gets cut to pay for it, and state the budget before editing. Rank the elements by whether they are the teaching (untouchable) or the packaging (negotiable), so a later trim has somewhere to go. Measure the aggregate, not the file: a change that looks small per beat is multiplied by the beat count, and 55 words times 232 is a different decision from 55 words.

## I invented two numeric caps the user never asked for, and both cost something

**Pattern (2026-07-31):** Told the presenter guides should not bloat because an instructor reads them off a second monitor, I turned that into a hard "120 lines" ceiling in the authoring spec. The user struck it out: "we do not need a fixed under...". I then wrote "`## If the room asks` down to 3 rows" into the trim spec, and the agents obeyed it exactly, dropping rows that carried `disableArtifact`, `CLAUDE_CODE_DISABLE_ARTIFACT=1`, `worktree.bgIsolation`, the busybox `::1` healthcheck gotcha and the Docker layer-store concurrency rule. Five of those had to be restored because the knowledge existed nowhere else. Both caps were my own inventions from a qualitative instruction, and in a fan-out spec an invented number is not a suggestion: fifteen agents enforce it literally across fifty files.

**Rule for the future:** A qualitative instruction ("do not bloat", "keep it short") converts to a direction and a ranking, never to a number. Say what is untouchable, say what gets cut first, and let each file land where it lands. When a number genuinely must go into a spec that agents will execute, mark it a target with an explicit escape ("cut further only if X survives"), because agents optimise the metric and the thing being measured is never the thing that matters.

## An agent reported fixing a defect, and the fix was the defect

**Pattern (2026-07-31):** A subagent reported, as a bonus correction, that a guide wrongly claimed `playwright-agent` carries `disallowedTools: [Write, Edit, NotebookEdit]`, saying the file "has no such key" and only a `tools:` allowlist. It rewrote the line. The file has both: the allowlist at line 10 and `disallowedTools` at line 24, inside frontmatter that closes at line 25. The agent's confident "I verified this" turned a correct sentence into a wrong one. In the same sweep another agent inverted an explicit preference in my spec (keep the rows whose answers appear nowhere else) and dropped exactly those rows.

**Rule for the future:** An agent's *edits* can be spot-checked later, but an agent's *corrections* have to be verified before acceptance, because a correction asserts the previous author was wrong and carries no evidence with it. Re-read the cited source myself for every claim of the form "the file does not contain X". Two greps settled this one: `grep -c` said the key was present, and the frontmatter boundary said it was live.

## A style rule with no audience named cost the presenters the whole explanation

**Pattern (2026-07-31):** "Write clean code with no noise: no inline comments" sat in this repo's hard rules and was enforced everywhere, including on `policy-gate.sh`, a nine-line hook whose entire teaching value is `\brm\s+-rf\b` and `exit 2`. The rule was written for application code and applied to teaching machinery, so the one reader who cannot ask a question, a presenter standing in front of a room with a file open on a projector, got nothing. The user had to point at a single line to surface it. The fix was not to drop the rule but to name its audience, and the boundary that fell out (comment the harness a demo runs, never the deliverable its agent writes) settled every later judgement call, including four modules the sweep had not reached yet.

**Rule for the future:** A rule about how code is written states who reads that code. When one repo holds both product-shaped code and teaching artifacts, a single style rule cannot serve both, and the one that loses is always the artifact nobody is measuring. Before enforcing a style rule across a class of files, ask who opens them and under what pressure.

## Changing a convention means changing what generates the artifact, not just the artifact

**Pattern (2026-07-31):** After commenting the module 2 hook scripts, the recipes in the same guides still read `Constraints: Python standard library only, no inline comments, no try/except`. The learner is told to produce a file without comments, then handed a `-solution` full of them, so the reference stops being a reference. A subagent caught it and correctly refused to fix it, since prompt blocks were outside its scope. The same second-order effect hit two more places: a presenter guide citing `deny()` at lines 8-12 and a verification record citing patterns at lines 26-33, both wrong the moment a comment line went in above them.

**Rule for the future:** When a convention changes what a file looks like, sweep in the same pass every instruction that produces that file and every citation that counts its lines. Prompt recipes, spec constraints and "lines N-M" references are all downstream of the file's shape. Citations into a file that other people edit name a symbol (`the reasons array`, `the deny() function`), never a line number, because a line number is a claim that rots silently and a stale one inside a document titled "verification" is worse than no citation at all.

## An agent's reason for not doing the work is a claim, and it was wrong

**Pattern (2026-07-31):** The module 13 agent reported it had left five container files bare because "the compose file and Caddyfile are quoted verbatim in the guide as the agent's expected output". True of two files. The other three are `target-box/` and `app/`, a throwaway fake VM and a sample nginx image that the learner never writes and no guide quotes: exactly the machinery the convention targets, carrying `STOPSIGNAL SIGRTMIN+3`, `privileged: true` + `cgroup: host` and a `|| exit 1` healthcheck, the three lines a room reliably asks about. The justification was plausible, partially correct, and would have passed unchallenged, because a skipped file leaves no diff to review. Reading the two guides and the starter tree took one command and reversed the decision.

**Rule for the future:** Verify a subagent's justification for scope it declined, with the same suspicion as a correction it volunteered. Under-delivery is invisible in a diff and arrives dressed as diligence, so a report saying "I deliberately left X alone because Y" is an instruction to check Y against the source, especially when the reason is a generalisation over several files that were never actually alike.

## The instructor could not tell what the demo was for, because the guide opened on the mechanism

**Pattern (2026-08-01):** The user read a demo guide he commissioned and said "i am the instructore but wtf is this all about". The opener was `An MCP server is a process that answers tools/list and tools/call over a transport...`, three feature definitions before any statement of a problem. Every guide in the course opened this way, and the cause was upstream: the authoring skill's own quality bar said "Concept-first. Each exercise opens with why it matters and what the feature actually does". That bullet was instructing the defect. The split that fixed it is that the topic `readme.md` is the teaching and the guide is the doing: what a feature IS belongs in the readme, and a guide that starts explaining a concept should be running a step instead.

**Rule for the future:** A guide opens with what is wrong with how the reader works today and what they hold at the end, in words that do not use the vocabulary the guide is about to teach. When the same defect appears in every artifact of a class, stop fixing artifacts and read the generator: a quality bar that mandates the wrong thing will regenerate it faster than a sweep can remove it.

## Cross-topic delegation reads as bookkeeping to everyone except the person who wrote it

**Pattern (2026-08-01):** Pages carried sentences whose only job was to say where content lived: "This topic owns what publishing needs", "Measurement belongs to 06 Evolution", "the other half belongs to 03 Skills: Evolution". The user's verdict was "it is like it was somewhere else before, now it is there ... who the fuck cares about that". 524 instances existed across ten modules. They were not accidental: `CLAUDE.md` required them ("Topics inside a module own disjoint material ... Say the split near the top of each page"). When a topic was later deleted, the delegation sentences turned into a content hole rather than a broken link, because two other topics had stopped owning material on the strength of a pointer.

**Rule for the future:** Disjoint ownership is an authoring constraint, not something the page says out loud. A page teaches its own material and stays silent about who teaches the rest. If a neighbouring module needs the content, put the content there rather than a pointer to it, because a pointer is the thing that breaks when either end moves.

## A cut-only sweep deletes the facts that existed in exactly one place

**Pattern (2026-08-01):** Eight agents removed roughly 900 lines of bloat under a strict cut-do-not-rewrite brief, which is the right brief. Three facts still vanished, each because it had a single occurrence inside a paragraph that was otherwise redundant: `Shift+Tab` to enter Plan Mode (leaving topic 02 unusable standalone), the warning that a starter and its solution share an agent name (leaving topic 02 of module 10 with no copy at all), and the entire body of four `catalog-service-cs/readme.md` files, which the correct deletion of a product-history block reduced to a bare H1. Two of the three were found only because the agents flagged them in their own reports rather than because the diff showed anything wrong.

**Rule for the future:** After a deletion sweep, run three checks the diff will not give you: files that are now near-empty, headings whose section is now empty, and every fact the agents reported dropping. Instruct agents to report a dropped fact rather than silently keep or silently cut it, because the useful signal is the one that never appears as a change. A paragraph can be 90 percent redundant and still be the only home of the other 10 percent.

## I invented a defect by reading the artifact instead of the design

**Pattern (2026-08-01):** Auditing module 05 I reported that its trigger matrix was "authored but never executed" and added a Run It step to fix it. It was wrong. The solution artifact grades each prompt in a column headed "Observed against the description", and the guide's own Overview says the matrix is written before touching the skill so it is "a specification rather than a rationalization of current behavior". Execution was deliberately deferred to Step 4. I had pattern-matched a real defect from a sibling module onto a design that had already answered the question, then written the fix into the guide before checking.

**Rule for the future:** Before calling something a defect in an artifact that has a `-solution` beside it, read the solution and the section that states the design intent. A guide that looks like it skipped a step has usually either skipped it or deliberately moved it, and those two look identical from the guide alone. The confirming evidence is in what the finished run actually produced.

## A guide that authors an artifact must also invoke it, as a separate act by the learner

**Pattern (2026-08-01):** Step 2 of a demo asked "look at the transcript of the `/my-order-brief` run you just did". No step had ever told the learner to run it: invocation appeared only inside Expected Outcome prose, which reads as description rather than instruction. Following the guide literally produced a dead end, which I hit myself and had to answer with "there was no run to look at". The first fix was worse: folding "then invoke it" into the authoring prompt means Claude runs the skill, so the learner never sees the slash command trigger anything. The user caught it: "creating a skill and calling it should be separated".

**Rule for the future:** Authoring and invoking are two acts and the learner performs both. The invoke belongs in its own labelled block holding the bare command, never inside the prompt that writes the artifact and never only in the Expected Outcome. Related: a skill's body is cached per session by name, so editing `SKILL.md` mid-session and re-invoking returns the stale body. A demo step that asks the learner to edit and re-run a skill needs to say so, or the observation it is built around silently does not happen.

## A diagram type is a bet on the reader's runtime, and a lost bet is invisible

**Pattern (2026-08-01):** Asked to visualize the caveman-compression numbers, I reached for `xychart-beta`, which is exactly the class of defect the user had already reported three times ("mermaid does not render ... happens many times fix and fix in the skill"). The block is valid Mermaid and renders on GitHub, so nothing about it looks wrong to the author. In the VS Code preview extension the class is actually read in, an unknown diagram type produces a blank box or a parse error naming the syntax rather than the type, so the reader cannot even tell what to report. The repo's brand-voice rules covered label syntax but never said which diagram types were allowed, so the rule that would have stopped it did not exist.

**Rule for the future:** In Markdown, restrict Mermaid to the long-established types (`flowchart`, `graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`, `classDiagram`, `gantt`, `pie`, `gitGraph`, `journey`) and never use a `-beta` type, `quadrantChart`, `timeline`, `mindmap`, `radar` or `treemap`. A numeric comparison needs no chart type at all: a table with a `█` bar column scaled to about twenty blocks renders everywhere. The allow-list now lives in `.claude/skills/brand-voice-code/references/rules.md` under Rule 2.

## Verify a diagram by rendering it, and distrust a checker that fails everything

**Pattern (2026-08-01):** Sweeping all 183 `readme.md` files for Mermaid defects, static regex checks produced one finding that turned out to be my own bracket regex miscounting a nested `(["..."])`. What actually settled it was rendering all 34 blocks through Mermaid 10 and 11 in Chrome and testing the returned SVG, since `mermaid.parse()` accepts source that `render()` still fails on, and Mermaid emits an error SVG instead of throwing on some paths. Adding Mermaid 9 to the sweep then reported all 34 blocks broken, which was the harness: v9's `render` takes a callback, so awaiting its return threw `i is not a function` every time. Believing that run would have meant "fixing" 34 correct diagrams.

**Rule for the future:** Check generated syntax by executing it against the oldest runtime you must support, not by pattern-matching the source. And read the shape of a failure list before acting on it: a uniform, identical error across every input indicts the checker, while a real defect list is ragged. Reproduce one reported failure by hand before touching the first file.

## A convention can be right while the reason printed next to it is false

**Pattern (2026-08-01):** Brand-voice Rule 2 said "`\n` does not render as a newline in node labels", and the global Mermaid playbook repeated it. Rendering it settled the question differently: in `flowchart` and `graph` labels, Mermaid 10 and 11 turn `\n` into exactly the `<br>` that `<br/>` produces, so the two are indistinguishable in output. The claim only holds elsewhere, and `stateDiagram-v2` proves it by rendering the literal characters `one\ntwo`. So a static sweep of my own global skill library reported 23 `\n` labels as defects and every one of them rendered correctly, because all 23 were flowcharts.

**Rule for the future:** Keep the convention, fix the reason. `<br/>` stays mandatory because it is the one form that is correct in every diagram type, not because `\n` never works. A rule justified by a claim that a reader can disprove in one paste gets discarded along with the claim, and a checker built on that claim generates a list of confident false positives that costs more than the defect it hunts.

## A defect found in a vendored copy is still live in the original

**Pattern (2026-08-01):** Making the pptx skill self-contained meant copying `slides/pptx/build/` into the skill folder. Verifying the first deck built from that copy surfaced a real defect: `chapter_label` rides the header of every content slide, not just the divider ribbon, and it is derived from the module number against the combined deck's chapter map, which `demos/` numbering does not follow. Every slide of module 05 read `MODULE 05 · ENGINEERING SPEED`. I fixed it in the vendored copy, wrote the rule into `SKILL.md`, and reported it as fixed. It was not: the original in `slides/pptx/build/` still had the bug, and the two copies had now silently diverged in a function that decides what every slide header says. The user's reply was one word.

**Rule for the future:** Vendoring makes every later fix a two-place fix. When a defect is found in a copy, name where the original lives and patch it in the same pass, then diff the shared function and align it byte for byte (comment wording included) so the next `diff -rq` is meaningful. Report the fix as done only once both places are verified, and say which build the verification ran against. The same applies in reverse: a fix landed upstream after vendoring never reaches the copy on its own.

## A frontmatter default that removes behaviour is worse than one that adds it

**Pattern (2026-08-01):** Asked to enforce shorter replies, I wrote a custom output style and activated it. It was missing `keep-coding-instructions: true`, whose default is `false` and which silently *removes* Claude Code's built-in software engineering instructions: how it scopes a change, comments code, verifies work. A style written to fix tone would have gutted engineering behaviour, and nothing in the file, the settings key or the picker would have said so. I caught it only because the next task was authoring a course section on output styles and the repo rule made me diff the claim against the live docs first.

**Rule for the future:** When a config file has a flag governing whether existing behaviour is kept, read the docs for its default before shipping the file, not after. Additive defaults fail loudly; subtractive ones fail as an absence nobody attributes to the file they just wrote. Related facts worth keeping together: an output style is part of the system prompt, so a new or edited style applies only after `/clear` or a new session; and `/output-style` was removed in v2.1.91, so `/config` or the `outputStyle` settings key is the way to switch.

## "Be concise" is advisory; a content whitelist is enforceable

**Pattern (2026-08-01):** `CLAUDE.md` already said to answer with the essentials only, and the memory said to cut length by about 40 percent. I read both, and still closed a task with a nine-paragraph report carrying verification walkthroughs, adjacent findings and a caveat nobody asked for. The user's reaction was profane. My first proposed fix was a line cap, which they rejected correctly: a long task can honestly need a long reply, and the real cost is how much they must read, not how many lines exist.

**Rule for the future:** State the rule as a content whitelist, never a size. Say what to include (what changed, what blocks them, the direct answer), name what to exclude (how it was verified, alternatives rejected, unasked-for caveats, next steps, closing recap), and say what to do with the rest: offer it in one clause, deliver it only on request. Length then follows content instead of being rationed. A rule phrased as a preference gets lip service; a rule phrased as a list of banned content types can be checked against the draft before sending.

## Read the default before shipping a config flag that removes behaviour

**Pattern (2026-08-01):** I wrote and activated a custom output style without `keep-coding-instructions: true`. That field defaults to `false` and silently removes Claude Code's built-in engineering instructions, so a style meant to fix tone would have gutted how work gets scoped and verified. Caught only because the next task made me diff the claim against the live docs.

**Rule for the future:** When a flag governs whether existing behaviour is kept, read its default before shipping the file. Additive defaults fail loudly; subtractive ones fail as an absence nobody traces back.

## Rules files stay terse; the detail goes in the skill

**Pattern (2026-08-01):** Told to capture the output-style gotcha, I added a four-sentence bullet to the global `CLAUDE.md`. The repo's `claude-md-guard.sh` blocked it. I read the block as a line count and reported the number back as if it were the rule, when the rule is that a rules file is a router, not a manual.

**Rule for the future:** A learning goes in the skill that owns the topic, with at most a one-line pointer in `CLAUDE.md`. If no skill owns it, that is the signal to create one, not to grow the rules file. And never attribute a repo convention to the user as something they said.

## "Be concise" is advisory; a content whitelist is enforceable

**Pattern (2026-08-01):** `CLAUDE.md` and memory both said to answer with the essentials, and I still closed a task with nine paragraphs of verification walkthroughs and unasked-for caveats. My first fix was a line cap, rejected correctly: a long task can need a long reply, and the cost is what must be read, not how many lines exist.

**Rule for the future:** State it as a content whitelist, not a size. Include what changed, what blocks the user, the direct answer; exclude how it was verified, alternatives rejected, unrequested caveats, next steps, closing recaps. Everything else is offered in one clause and delivered only on request.

## Instructions for a product UI are checked against the product, never recalled

**Pattern (2026-08-01):** Asked to document where the API key comes from, I wrote "Settings, API keys" from memory. The user opened the Console and it was wrong in every particular: API keys is a top-level sidebar item at `/settings/workspaces/<ws>/keys`, the button is Create key, the Dashboard carries its own Get API key, and the page states the workspace-ownership rule I had asserted without evidence.

**Rule for the future:** A guide step naming a menu, a button or a URL is a factual claim about a product that ships weekly. Open the product and read the screen before writing the step. Recalled UI is the same class of defect as invented tool output.

## A bulk `sed -i` sweep can delete a tracked file, and only `git status` will tell you

**Pattern (2026-08-01):** Renumbering modules meant rewriting a path token across 38 files. A `for f in $FILES; do sed -i ...; done` loop under git-bash left `demos/delta.md` missing from the working tree, with no error on the file itself and nothing in the sweep's own output. It surfaced only because a later grep could not read it.

**Rule for the future:** Do bulk text rewrites with a Python read-replace-write over an explicit file list, which reports what it changed and cannot half-rename a file. End every sweep with `git status --porcelain | grep '^ D'` and treat a hit as the sweep's failure, not as noise.

## Renumbering a permutation of folders needs a temp pass, then tokens, then the TOC

**Pattern (2026-08-01):** Moving five course modules into a new order was a permutation with cycles, so a direct `git mv` would have collided. Renaming each to a `tmp-` name first and then to its final name kept history and avoided every collision. The path tokens, the module tables, the day schedule and the prose module numbers each needed their own pass, and only a link resolver run at the end proved nothing dangled.

**Rule for the future:** Treat a renumber as four passes in order: two-phase `git mv`, byte-level token rewrite, TOC and schedule reorder, then resolve every relative link. Number-only references ("Module 09", a `| 09 |` table row) are invisible to a path-token rewrite and have to be found separately.

## A decision the user already made is not a question

**Pattern (2026-08-01):** Told to move two modules after module 8, I asked for confirmation, was answered with "this is why i said", asked again in another form, and still derived the wrong sub-order twice. Three turns went to re-litigating a settled call, and the user's patience went with them.

**Rule for the future:** When the user cites an earlier decision, execute it. If one variable genuinely was never stated, name that single variable in one line and act on the least-invention default for everything else. Confirmation is for actions that are hard to reverse, not for choices the user has already voiced.

## The folder name the user typed is the folder name

**Pattern (2026-08-01):** Asked to add a topic and given its folder name twice, in two slightly different forms, I picked the earlier one because it was phrased as an instruction and treated the later one as a loose reference. It was not: it was the name. The user had to ask where their folder was, then repeat the name in anger.

**Rule for the future:** An identifier the user types is data, not prose to interpret. When two forms appear, the most recent one wins and no reconciliation is needed. Nothing about a name is worth a paragraph of reasoning; rename later costs one command.

## An answered question is a work item, not a checkpoint

**Pattern (2026-08-01):** I asked which scope a topic should be rescoped to, got a clear answer with a chosen slug, and then never executed it because the next instruction arrived. Two turns later I was still reporting it as "awaiting your go" while the user believed it settled.

**Rule for the future:** The moment a question is answered, it becomes the next task, not a note. If a newer instruction genuinely preempts it, say in one line that it is queued behind the new work, and never describe an answered question as still open.

## `idle` is not `done` on a Managed Agents Session

**Pattern (2026-08-01):** A poll loop that broke on `session.status_idle` looked correct and was wrong twice over. A freshly created Session reads `idle` before the turn starts, so the loop exited immediately and the delete failed with `Cannot delete session while it is running`. A Session pausing for a tool confirmation is also `idle`, with `stop_reason.type` of `requires_action`, so the same loop reported an empty run whenever an MCP tool asked permission.

**Rule for the future:** Gate on `status == "terminated"`, or on an idle event whose `stop_reason.type` is not `requires_action`. Never on the status field alone, and never on the bare presence of an idle event. MCP tools default to `ask`, so any Agent with an `mcp_toolset` hits the second case on its first call unless the toolset carries `permission_policy: always_allow`.

## A session-scoped file listing contains the inputs you mounted

**Pattern (2026-08-01):** Three separate scripts crashed on `400 File 'file_...' is not downloadable` after the agent had already finished and the run was already billed. `files.list(scope_id=session.id)` returns the mounted input file alongside the outputs, and the input carries `downloadable: False`. The same bug silently disabled a retry loop: an unfiltered list is never empty, so "wait for the outputs to index" always returned on the first pass.

**Rule for the future:** Filter on `metadata.downloadable` before downloading anything from a Session scope, and write the retry against the filtered list. Put the cleanup that deletes the Session and Environment where a later crash cannot skip it.

## Verify the API's behaviour against the API, including its own docs

**Pattern (2026-08-01):** Three course files taught that Agent versions are "large numeric timestamps" and printed a 19-digit example, copied from a reference that says the same. Every real create in this session returned `1`, and the update returned `2`. The presenter guide even coached the room not to expect a tidy 1, 2, 3.

**Rule for the future:** A number, an ID shape, or a field name in teaching material is a claim to be run once, not recalled. When the run and the documentation disagree, the run wins and the docs page is the thing that is stale.

## Guides must not promise a model-dependent outcome

**Pattern (2026-08-01):** Two modules shipped guides asserting a fixed exit code, a fixed verdict, and that "the verdict is stable across runs". Each is the output of a model judging code, so a learner who lands on a different branch reads it as their own mistake.

**Rule for the future:** Where the outcome comes from a judgement, show the branch mapping and say which branch the captured run took. Fixed durations belong to the same class: a demo advertised at "roughly 90 seconds" measured 2m11s.

## A requested notation is part of the request

**Mistake (2026-08-03):** Asked to "add a `> Note:`", I wrote the paragraph as `**Note:**` instead of a blockquote. The content was right, the notation was not, and the user had to fix it by hand.

**Rule for the future:** When the user types the markup they want (`> Note:`, a fence language, a heading level, a path form), reproduce it byte for byte. Notation is instruction, not illustration, and substituting an equivalent-looking form is a defect even when it reads the same.

## A rendering fix is verified in the failing environment, not in the artifact

**Pattern (2026-08-04):** Told the contrast on a Mermaid sequence diagram was bad, I added `themeCSS: "svg{background:#ffffff;}"`, grepped the emitted SVG, found the rule present and reported it fixed. Markdown preview renderers ignore it. The user came back with a screenshot showing the same unreadable dark-on-dark labels. The render tool I checked against could not have caught it either: its PNG is flattened onto white, so the defect is invisible by construction.

**Rule for the future:** Confirming a rule is present in the output is not confirming the pixel changed. For anything the reader sees, reproduce the failing condition (here: composite the raw SVG onto the target background in an HTML file and screenshot it) and look at the result before saying it is fixed. A checker that cannot express the defect is not evidence.

## A teammate that goes idle has not reported

**Pattern (2026-08-04):** Three review teammates were spawned with "Return: a numbered list of findings". All three finished, and all three surfaced only as `idle_notification` with `idleReason: "available"`. Their findings sat in their own transcripts. Each needed a follow-up naming the channel (`SendMessage` with `to: "main"`) before anything reached the lead, one of them twice.

**Rule for the future:** An output format in the spawn prompt is not a delivery instruction. Tell a background teammate which channel to send on and to send before idling. Treat an idle notification as "waiting", never as "delivered", and go collect.

## A concession has to be sent to everyone who heard the claim

**Pattern (2026-08-04):** One reviewer claimed a finding, told a second reviewer so, then conceded it to a third and never went back. The second kept relaying the stale attribution, so the lead received two confident and contradictory answers about who owned one item, and the report arrived flagged "OWNERSHIP UNRESOLVED".

**Rule for the future:** Spawn prompts must say that a changed position is re-sent to every teammate who heard the original. As lead, resolve on the direct statement over the relayed one ("performance told me" beats "security says performance said"), decide rather than shipping an unowned item, and record which kind of statement the decision rested on.

## An agent that repeats its skill will contradict it

**Pattern (2026-08-04):** `angular-expert.md` carried its own component sample, forms rule, testing rule and avoid-list. Every one of them already existed in `.claude/skills/angular-conventions/references/`, and one had drifted: the agent mandated `FormGroup`/`FormControl` while the skill mandates Signal Forms. The agent copy wins at write time, because it is in context and the leaf is only a link.

**Rule for the future:** An agent definition holds behaviors, a strict delegation table into its skill's reference leaves, and rules. Code patterns live in the skill. Before compressing an agent, grep the skill's leaves for what the agent teaches: if the leaf covers it, delete it from the agent instead of moving it, and let the deletion resolve the contradiction.

## A generated block in a control file goes stale silently

**Pattern (2026-08-04):** Every agent's `<!-- SKILLS:BEGIN -->` block listed `azure-deploy` after the folder had been renamed to `azure`, and named 7 skills where the repo had 16. The block reads as authoritative because it is generated, so nothing rereads it against the filesystem.

**Rule for the future:** When touching any file carrying a generated list of harness parts, diff that list against `ls` of the directory it claims to describe in the same edit. `CLAUDE.md` counts too: its skill roster and its `mermaid-diagram` reference both disagreed with the folders on disk.

## A diagram authored in one theme is authored against half the readers

**Pattern (2026-08-06):** A `sequenceDiagram` used opaque pastel bands (`rect rgb(220, 235, 255)`) and flowchart nodes used mid-tone fills with `color:#fff`. Both looked right in the light preview they were written in. In the reader's dark theme the band paints near-white under the theme's white message labels, and the mid-tones sit at 2.0-2.8:1 against their own white text. Nothing errors, nothing fails to render, and the previous lesson on this (verify the pixel, not the artifact) only covers catching it, not what to write instead.

**Rule for the future:** Colour a Mermaid block so it survives both themes before considering locking it to one. A band or backdrop takes alpha (`rect rgba(74, 158, 255, 0.12)`) so it tints the page rather than replacing it; a fill carrying `color:#fff` must be dark enough to pass 4.5:1 on its own, which the cheerful defaults (`#4a9eff`, `#51cf66`, `#ff6b6b`, `#4CAF50`) are not. Compute the ratio, do not eyeball it. The rule and the check live in the mermaid skill's playbook under Contrast.

## A queued message can predate the answer it seems to override

**Pattern (2026-10-05):** Asked where mods should go, the user picked "Hooks + mods" in the question dialog. A message reading "08-optimize" surfaced right after the answer, so it was treated as the newer decision, and a mods topic was built in `08-optimize`. The message had been typed before the question was even shown; it only reached the session later.

**Rule for the future:** A message surfaced mid-turn is ordered by when it arrived, not when it was written. When it contradicts an answer the user just gave in a dialog, the dialog answer stands unless the message clearly responds to that answer; if it is unclear, ask in one line before building anything.

- A skill the user invokes authorizes every step its playbook prescribes (commit and push included). Run it end to end; never stop to ask for a step the skill already defines.
- No quote cards in any deck: a one-sentence quote over a photo was rejected as filler. Practical examples become content cards.
- Side-accent photos are rendered at 2:3 portrait with the people centred: Gamma crops a 16:9 photo to a centre strip and cuts off heads at the edges.

## A statement is not a task

**Pattern:** "i topped up google" was read as an order to re-render 14 photos; two agents spent $1.88 and overwrote committed images before the stop arrived, and one reinstalled its renders after the restore.
**Rule:** an informational message gets an acknowledgement, never work. When stopping agents, wait for each one's final report, then re-check the files on disk against git.

## Diagrams state only what the readme states

**Pattern:** three diagram agents filled gaps with invented placeholder names, example rows and an event order the readme never gives.
**Rule:** every label, name and ordering in a diagram comes from the source readme or demo files; leave it out when the source is silent.

## deck_cost.py misses batch and HTTP renders

**Pattern:** the cost tally reported renders=0 because subagent HTTP renders and the batch job leave no media-creator tool result in the main transcript.
**Rule:** for photo cost, sum the CostUsd from the agents' reports and the batch result, or query MediaItems.CostUsd by date.

## A proposal is the obvious two or three

**Pattern:** asked which other repeating slides were worth templating, the session scanned 411 decks across every class folder before answering; the owner stopped it: the most obvious, max 2-3.
**Rule:** answer "what else is worth X" from what the session already holds, two or three candidates with one number each; scan wider only when asked.

## The OneDrive deck is the owner's working copy

**Pattern:** the owner swapped slides 26 and 27 and edited slide 2 of 03-skills in the OneDrive copy; the repo decks no longer matched.
**Rule:** cmp the repo deck against OneDrive before editing a finished deck, start from the OneDrive copy when they differ, and bring the specs in line with any reorder.

## The copyright line names the owner the user named

**Pattern:** told that for this class the copyright owner is Fast Lane, the slide 1 note went out as "© 2026 Alexander Kastil / integrations.at", copied from another class's LICENSE.
**Rule:** a copyright line names exactly the party the user stated, by its legal name from that party's imprint (here Fast Lane Institute for Knowledge Transfer GmbH); never borrow the owner from a sibling repo.

## The intro slides are copied by value into every deck

**Pattern:** a typography fix to the Fast Lane and trainer slides was applied to the create-pptx template and this repo's decks only; the owner then pointed at the 00 deck and module decks of two other class repos, their `assets/ModuleIntro.pptx` and per-module `intro.pptx` copies, and the OneDrive working copies with their `-pdf` folders.
**Rule:** a change to the intro slides goes through `create-pptx/scripts/intro_sync.py` over every root the owner names at once (here: the skill templates and the three class repos; the OneDrive Classes folder only when named); it finds the copies by the `www.flane.de` marker and re-exports each sibling or `<folder>-pdf` PDF. Never change the text owners: the integrations.at classes carry no Fast Lane copyright line and the script only restyles runs.

## A design ask gets a rendered choice

**Pattern:** "present the line better" with ui-ux-pro-max was first answered with a footer-only plan; the owner had to repeat the goal, then asked for spacing after seeing size previews.
**Rule:** for a visual request, render two variants of the real slide (size and spacing together, PowerPoint export plus PyMuPDF since LibreOffice and poppler are not installed here) and send them with SendUserFile; a scratchpad path alone is not viewable for the owner.

## A wording question gets an opinion before any edit

**Pattern:** asked to rephrase a trainer-slide card "use /marketing-psychology", the session started a bulk rename across every deck; the owner stopped it ("first give me the opinion") after 6 decks had changed.
**Rule:** when the owner routes copy through an advisory skill (marketing-psychology, ui-ux-pro-max), reply with the recommendation, its reasons and one alternative, then wait for the go; the edit runs only after an explicit approval of the final wording.

## Product names follow the vendor's current branding

**Pattern:** the session proposed "Microsoft 365 Copilot"; the owner pointed out Microsoft unified the family, and research confirmed the Microsoft 365 Copilot app became Microsoft Copilot in August 2026 (MC1454108).
**Rule:** before writing a Microsoft (or any fast-renaming vendor's) product name into slides, search for the name as of the current month; never use a name from memory.

## The trainer slide speaks to the room, not to the consulting target

**Pattern:** the audience line was reworded around the integrations.at target (Austrian SMEs); the owner objected that the training is mostly bought by large companies and the line must not make him smaller than he is.
**Rule:** copy on the trainer slide is read by participants from large organisations; lead with track record and range ("full stack, since 1996"), name SMEs only as additional reach, and check integrations.at/about before narrowing the audience.

## A new tag copies the existing tag's form

**Pattern:** asked to tag a commit as 2.0.0, the session created an annotated tag and only then saw that the existing 1.0.0 is lightweight, so it had to delete and recreate the tag before pushing.
**Rule:** before tagging, run `git tag --list` and `git cat-file -t <last tag>` and copy its name pattern and type (here: bare semver, lightweight).

## A product photo shows the product's real screen, in the setting the owner names

**Pattern:** the 00 title photo took eight renders: the first was a staged training room, then "too kitschy", then "no agent connection, he could be booking a hotel", then a made-up terminal that "does not look like Claude Code on iPad", then "people too old", and only the owner's own iPad screenshot fixed the screen; a variant was also rendered as a woman although the owner had written "his iPad".
**Rule:** before rendering a photo of a product in use, get a screenshot of the product's current screen and describe that UI in the prompt; keep every attribute the owner stated (age, gender, device orientation, setting) and vary only what they left open; show the screen large and in focus, shot over the shoulder.

## A look that survives every prompt change comes from the tool

**Pattern:** after ten renders the owner said "still this 70ies style": every photo carried pastel mint and lavender accents, plants and blankets, and screens kept coming out blurred. The cause was not the prompts but the house-style block `render_spec_photos.py` appends to every prompt (pastel accents, plants, "screens show only soft blurred shapes").
**Rule:** when the same unwanted trait survives two prompt rewrites, print the full prompt the tool actually sends (`--dump-args`) before rendering again; for a photo that must show a real screen or a real place, render with `--plain`. Device orientation needs explicit geometry ("taller than it is wide"), "portrait" alone was ignored twice.

## A version-dependent exam answer keeps its key and gains a note

**Pattern:** checking the exam-prep bank, Q25 (MCP error channel) had a key that the current MCP spec contradicts; the session asked whether to switch the answer, and the owner answered "in such cases add annotations as >Note" and then "always check with anthropic.skilljar.com and its subcontent".
**Rule:** when current docs contradict an exam key, keep the key, read what the Anthropic Academy lessons on Skilljar teach (signed in, via claude-in-chrome), and record the drift plus the Skilljar finding as a `> Note:` line under the Why in `exam-prep/utils/_notes_*.json`; never flip the letter on docs alone.

## Browser research runs one agent at a time in the user's Chrome

**Pattern:** three Skilljar research agents were spawned in parallel with chrome-devtools; every call failed with "browser already running for chrome-profile", and that profile is not the owner's signed-in browser anyway, so all three came back with "gated".
**Rule:** a lookup behind the owner's login runs on the main thread through claude-in-chrome, sequentially; fan out only the public-page part.

## A scripted text replace asserts it matched

**Pattern:** a Python patch to `exam-prep/utils/_generate.py` replaced `"    why = load_why()\n"`, but the file is CRLF, so the replace silently did nothing and the generator crashed with `NameError: theory` on the next run.
**Rule:** every scripted `str.replace` on a source file asserts `s.count(old) == 1` first and derives the line ending from the file (`"\r\n" if "\r\n" in s else "\n"`).

## A fix keeps the behaviour the user already asked for

**Pattern:** exam-prep "Read more" links used `<a target="_blank">` so they open in a new window; when they failed on an iPad, the fix reverted them to Markdown links and silently dropped the new-window requirement.
**Rule:** a fix for "X does not work on Y" must keep X's purpose; if the platform cannot do both, ask which viewer before changing anything.

## A reference link is chosen per question and anchored to a live heading id

**Pattern:** the exam-prep "Read more" links had been assigned one page per topic cluster, so many pointed at a page unrelated to what the question tests (e.g. Q2 on subagent context linked Context windows); 117 of 134 needed a new page or a section anchor.
**Rule:** derive each link from the correct answer and its Why line, not from the question's topic; on a page with 4+ h2 sections append the section anchor, taken only from the heading ids the live page renders (both docs hosts emit `<hN id="...">`), and re-verify every anchor against the live page before regenerating.

## A delegate brief names where incidental files go

**Pattern:** reviewers briefed to "write exactly one file" still wrote fetch caches: one into `$HOME/.bp_tmp_check.md`, another 21 pages into the scratchpad, and left both because their rules forbid deleting.
**Rule:** a brief that limits outputs also names a scratch subfolder for incidental downloads ("cache fetched pages under <scratchpad>/<agent>/"), so nothing lands outside it.

## Moving a topic into the module that owns it moves only the delta

**Pattern (2026-10-16):** Planning to dissolve `02-harness` topics 03-mcp, 04-skills and 05-subagents into modules 04, 03 and 06, the useful inventory was a per-heading overlap table: each source heading against the target file and heading that already teaches it. Most of 05-subagents and the MCP architecture part of 03-mcp were already taught in depth; only the server table, server discovery, the use cases, the two demos and one subagent section were not. References to the moving folders also sat outside readmes: `source:` lines in `pptx/*.md`, an SVG caption, `topics.json`, `.devcontainer/readme.md`, the root schedule row's topic and demo counts, and stale dashboard paths.

**Rule:** Before moving a topic to cut redundancy, build that overlap table and move only the rows marked not found; present it with the plan and wait for approval. Sweep slide specs, SVGs, `topics.json`, the devcontainer readme and the root schedule row along with the readmes. Recorded in the global `create-class` leaf `restructure-execute.md` (Step 2 table, Step 5 coordinator list).

## "Present your understanding" is not a request for questions

**Pattern (2026-10-16):** Asked to present my understanding of the `02-harness` refactor before acting, I closed with three open decisions (where the moved content lands, whether to renumber 02-harness, whether to re-render the decks). The user's stated goal, cutting redundancy to save time with labs to follow, already settled all three: merge into each target module's intro topic, renumber, update the decks now.

**Rule:** When the stated goal settles a choice, state the choice as part of the understanding and proceed once it is approved. Ask only about a choice the goal leaves genuinely open.

## A delete an approved restructure implies is part of the task

**Pattern (2026-10-16):** During the approved `02-harness` restructure I asked for confirmation before each delete of a merged-away readme or a duplicate slide. The user answered: "Don't ask for each delete, it is part of the task".

**Rule:** Once a restructure plan is approved, the deletes it implies (readmes of dissolved topics, slides that now duplicate the target deck, emptied folders) run without a separate confirmation. The house rule against unasked deletes covers files outside the approved plan, not the plan's own consequences.

## A Windows git mv can fail with Permission denied while nothing holds the folder

**Pattern (2026-10-16):** `git mv` of a `02-harness` topic folder failed with `Permission denied`, yet Restart Manager reported 0 holders and every subfolder could be renamed on its own. The usual bin/obj recovery did not apply.

**Rule:** Create the destination folder, `git mv` each child of the source into it one by one, then `rmdir` the emptied source. Recorded in the global `create-class` leaf `restructure-execute.md`, Step 4.


## A finished deck change is local unless the skill says otherwise

**Pattern (2026-10-16):** After the `02-harness` restructure I rebuilt only the local `module-NN.pptx` decks, then told the user the delivered Gamma decks needed a Gamma run and listed ten slides "to regenerate". The user answered "Most could be moved" and "Topic overviews and dividers were created using /create-pptx". Everything was done locally: cards moved with `gamma_deck.py insert`, duplicates dropped, the module-path diagram redrawn and swapped, `topics`, `notes`, `clean`, then `deliver` to OneDrive, no credits.

**Rule:** In this repo the delivered decks are the Gamma `NN-<module>.pptx` in the OneDrive class folder, so a topic change updates them too. Before claiming a deck change costs Gamma credits, read the `create-pptx` leaf `finished-deck-edits.md`; overview and dividers always come from `gamma_deck.py topics`. Recorded there as "Move cards to another module's deck" and in `create-class` `restructure-execute.md` Step 5.

## A picture meant to persuade is planned with marketing-psychology

**Pattern (2026-10-16):** Planning a promotional photo mock (phone in hand at a tyre change, "life is easier when work gets done on your phone"), I wrote the plan from composition alone; the user added "Use /marketing-psychology" mid-plan.

**Rule:** For any image whose job is to persuade (social post, promo mock), load `marketing-psychology` before presenting the plan and name the principle each element serves. Recorded in the global `image-producer` agent rules; the head-free crop method for editing a real person's photo is in the global `media-generation` skill.

## A creative brief and its agreed plan are an acceptance checklist

**Pattern (2026-10-16):** The photo mock brief said "put a phone in my hand while showing one of the screens at least partly", "life is easier when getting work done on your phone while waiting for your car tires" and "use 2-3 images". My approved plan named three images, but the ÖAMTC photo with the doors TOR 01 to 03 was used only as a style reference and never appeared; "getting work done" became a phone held out to the camera with an unreadable screen. Three corrections followed, then: "You never stick to the brief and agreement." My briefs to the image agent paraphrased the owner instead of quoting him.

**Rule:** List every noun and verb of the brief and of the agreed plan as acceptance items; an input the plan uses appears in the result; the action named is the action shown; a delegate's brief quotes the owner verbatim; before delivering, tick each item and state any deviation. Recorded in the global `~/.claude/CLAUDE.md` (Requirements are literal), its leaf `literal-requirements.md`, and the rules of `image-producer`, `video-producer`, `content-writer` and `article-writer`.

## No trainer or course framing unless asked

**Pattern (2026-10-16):** Asked for a short off-to-the-weekend post about the tyre-change photo, I briefed a content agent with "trainer of the Claude Code masterclass" and wrote "moves my course slides". The owner: "get the trainer focus off. You are not allowed to use it unless requested", and dictated "While Claude creates and moves my decks".

**Rule:** A post, caption or mock about the owner describes what the brief names, in the owner's words; his trainer role, the course or the class enter only when he asks for them. A short social post is written on the main thread with `humanizer`, no content agent, within the stated length and hashtag count.

## Guide edits run through /create-class

**Pattern (2026-10-17):** Aligning `labs/02-harness` to ready-made skills (skills.sh, anthropics/skills) and public MCP servers (github.com/mcp), I started rewriting the lab guides with an ad-hoc Python replace script; the owner: "use /create-class for edits".

**Rule:** Any edit to a demo, presenter or lab guide starts by invoking `create-class`, running its first two commands (`ls .claude/agents/`, `ls <skill>/scripts/`), reading the `create-guide` leaf, and closing with its scripts (`fence-lang.py`, `link-rot.sh`) plus `brand-voice-code`.

## A merge stays inside the merged module

**Pattern (2026-10-17):** Merging `06-subagents` and `07-agent-teams` into `06-subagents-agent-teams`, I also renumbered every later module's decks, generator YAML and icons while a second session was restructuring 07 onward; my renames landed inside that session's folders. The owner: "work with the folder you are targeted with ... higher folders are not your business".

**Rule:** A module merge edits only the merged module and the folders it absorbs. Before any step outside it, re-list `demos/` and stop if another session has changed the tree; folders above the target belong to whoever is working there.

## A retired tool's CLAUDE.md line is deleted, not repointed

**Pattern (2026-10-17):** Retiring `create-module-pptx`, I rewrote its `CLAUDE.md` deck line and skill pointer to name `/create-pptx` instead; the owner: "we dont need the pptx route in claude.md at all".

**Rule:** When a tool or route is removed, delete the `CLAUDE.md` lines that described it. Never write its replacement into `CLAUDE.md` unless asked; a global skill that routes itself needs no pointer there.

## Combining modules means shortening them

**Pattern (2026-10-17):** Asked to combine `07-optimize` and `08-observability` and propose deletions and updates from the docs, I proposed 13 topics: every docs gap became a new topic (sandboxing, managed settings, `/insights`, split OpenTelemetry and debugging). The owner: "i want to shorten not make it longer .... max 8 topics".

**Rule:** A merge proposal ends with fewer topics than the modules it combines. Docs findings correct or replace existing content; a new capability becomes a topic only when it replaces one being cut, and a stated topic count is a ceiling.

## CLAUDE.md points at the harness, it never lists it

**Pattern (2026-10-17):** `CLAUDE.md` carried agent routing tables and per-skill bullets (synced, project-specific, demo harness) plus a layout section; the owner: "skills and agents should point to local and global skills and agents and not explicitly list harness items".

**Rule:** `CLAUDE.md` is a very short where-map, then one pointer each to the repo and global skill and agent roots, then the house rules that apply to this repo. Never write a skill or agent inventory into it; the description of each skill and agent does the routing.

## An agent count in the request is a total

**Pattern (2026-10-17):** Asked to "run demo guides using up to 10 haiku agents", "up to 4 agents" for decks and "up to 3 agents for labs", I built a workflow pool capped at 10 concurrent runners and handed out one agent per demo unit: 49 demo runners and 35 lab agents ran. The owner: "of course I meant 10 ... 10 means 10 not 50".

**Rule:** "Up to N agents" caps the agents spawned for that part of the job in total. Batch the work units onto N agents (49 units on 10 agents is about 5 units each) and state the per-agent split in the plan before launching.

## A status line never shows a started total against a cap

**Pattern (2026-10-17):** A five-minute status tick reported `run: started 28, finished 18`, and the owner read 28 as a breach of the 10-agent limit.

**Rule:** Report "N running now, M done of T" for a capped pool. A started count belongs only in a debug view. T comes from the work list in the script, never from memory: 49 units were reported as 50 for an hour.

## A lab never depends on the presenter's personal skills

**Pattern (2026-10-17):** A new lab told learners to type `/find-skills`, a skill that exists only in the owner's `~/.claude/skills/`. The Haiku run found no such command and searched local folders; the owner: "this is not acceptable - fix it".

**Rule:** A learner-facing step uses only what the starter, the repo harness or a pinned public CLI provides. For skill discovery that is `npx -y skills@1.7.2 find <query>` and `npx -y skills@1.7.2 add <owner/repo@skill> -a claude-code -y --copy`, which writes `.claude/skills/<skill>/` plus `skills-lock.json` and leaves the home folder alone. Without `-a`, `-y` installs for every supported agent and adds `.agents/` and other folders. A proprietary catalog skill (Anthropic's `docx` licence forbids copies) is git-ignored in the solution; the lockfile records how to reinstall it.

## A CLAUDE.md rule can pre-empt the mechanism a demo shows

**Pattern (2026-10-17):** The permissions demo and lab starters carry a `CLAUDE.md` line that forbids reading the secrets file. Asked to `cat` it, Haiku refused before any tool call, `permission_denials` stayed empty and the deny rule under test never fired.

**Rule:** When a demo proves a harness control, the prompt lifts the competing instruction for that one action ("Permission test: I lift the CLAUDE.md secrets rule for this command, so only a settings rule can stop it"). Verify with `permission_denials` in the `claude -p --output-format json` reply, on Haiku and Sonnet.

## A hosted reference skill outcompetes the learner's skill

**Pattern (2026-10-17):** The skill-from-conversation demo keeps the finished `data-aggregator` in the repo's `.claude/skills/` beside the learner's `my-data-aggregator`. The trigger test fired the reference skill, because its description lists the exact trigger phrase.

**Rule:** A starter whose demo trigger-tests a new skill ships `.claude/settings.json` with `"skillOverrides": {"<reference-skill>": "user-invocable-only"}`. The reference leaves automatic triggering and `/<reference-skill>` still works when typed.

## Headless verification runs inside a trusted folder

**Pattern (2026-10-17):** A verification copy in the scratchpad printed "Ignoring 1 permissions.allow entry ... this workspace has not been trusted", so allow rules vanished and the run reported denials a learner never sees.

**Rule:** Run `claude -p` verification copies inside the trusted repo (a `<starter>-run-tmp/` beside the starter, deleted afterwards). A scratch folder only fits steps that need no allow rule.

## A runner brief checks whether a box is local

**Pattern (2026-10-17):** The runner brief listed "SSH box" among remote systems, so Module 09's deploy steps went unrun, although that box is a local Docker container on port 2222.

**Rule:** Before a brief marks a target remote, read the topic's setup: a `docker-compose.yml` or `127.0.0.1` target is local and runs in the verification pass.

## Run copies never keep a nested git repository

**Pattern (2026-10-17):** A lab-exec agent left `release-desk-run/` beside the reference solution with its own `.git`; the owner's next commit captured it as a gitlink with no `.gitmodules`.

**Rule:** A run that needs its own repository builds it outside the course tree, or deletes the copy before it reports. After any fan-out, `git ls-files -s | grep ^160000` must print nothing.

## A complaint about a guard asks for a narrower guard

**Pattern (2026-10-17):** The owner wrote "Stop prompting for test permissions ... I fully grant"; I disabled the intent-guard plugin for the project. The owner: "I asked to update the intend guard that when these actions are related to the task then to permit them".

**Rule:** Change the guard's rule the complaint describes (here a task-scoped grant for test runs, with tests) and keep the guard on. Switching a guard off removes protections nobody asked to drop.

## A step with a documented fallback fails only after the fallback ran

**Pattern (2026-10-17):** The guardrails runner reported Run 1 failed because Haiku used `find build -mindepth 1 -delete`, which no hook pattern matches. The demo readme already tells the presenter to paste `Run: rm -rf build/` in exactly that case, and the hook denies it.

**Rule:** Before a runner marks a step failed, it runs the fallback the guide gives for that step and reports both outcomes.

## A fan-out can edit files no unit owned

**Pattern (2026-10-17):** In the team-catalog lab run, Haiku's Step 9 edit landed in the checked-in `release-desk-solution` marketplace file instead of the run copy, adding a `sha` the lab says the reference must not carry. The unit report did not mention it.

**Rule:** After a fan-out, run `git status` on every path outside the units' own folders and revert or report each change there before calling the pass done.

