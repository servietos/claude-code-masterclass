# Run the Same Feature Through Spec Kit and BMAD-METHOD

Build the same `notes-cli` feature from Lab 01, but driven by two packaged spec-driven frameworks: GitHub's [Spec Kit](https://github.com/github/spec-kit) and the [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD). The goal is to see how each tool formalises the workflow you ran by hand: what they generate, what they assume, and where they differ.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code (or a shell command, where noted)
- **Expected result**: what the outcome looks like

> **Prerequisite:** Complete [Lab 01](lab-01-spec-driven-from-scratch.md) first. You should have a working `notes-cli/` folder with a `STATE.md` that describes the tag-and-pin feature. This lab uses the same feature so you can compare the two approaches side by side.

> **Version note:** Part A follows `specify-cli` 1.2.1, the release the module's Spec Kit topics were recorded against, and Part B was verified against `bmad-method` 6.10.0 on Windows with git-bash. Both tools move fast. If a command name below does not appear after install, re-read the tool's own post-install output: it prints the current command list.

The starter for Part A is already in this repo at [02-tooling/notes-cli-speckit/](02-tooling/notes-cli-speckit), holding the `.gitignore` that keeps the generated trees out of the course repo. The finished reference lives beside it in [02-tooling/notes-cli-speckit-solution/](02-tooling/notes-cli-speckit-solution): the same `.gitignore`, plus the `.specify/` and `.claude/` trees `specify init` generated there, which that ignore file deliberately keeps out of version control. Run the setup yourself, then compare.

> **Installer footprint:** Both installers write into the folder you run them in, including that folder's `.claude/skills/`. Run them in a **project folder of their own**, never at the root of an existing project and never at the root of this course repo. Spec Kit adds 10 skills; BMAD adds 46. Spec Kit even prints an "Agent Folder Security" panel advising you to gitignore `.claude/`, because agents may store credentials there.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/11-planning/02-tooling/notes-cli-speckit
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `notes-cli-speckit` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/11-planning/02-tooling/notes-cli-speckit write compare-vs-manual.md with the tokens, files and verdict sections ....
```

That works for any step whose result is just files. It does not work for the skills the installers write: `specify init` puts 10 and `bmad-method install` puts 46 into the `.claude/skills/` of the folder they run in, and a slash command like `/speckit-specify` exists only for a session launched there. Launch inside `notes-cli-speckit` from Step 1 onward.

Launching inside the starter makes the lab folder the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

That is the Part A starter, already checked into this repo. Part B installs BMAD into a second fresh folder beside it, `labs/11-planning/02-tooling/notes-cli-bmad`, and opens its own session there. Stand inside the matching project folder before you run either installer: pointed at the course repo root, `specify init` and `bmad-method install` would write their 10 and 46 skills straight into this repository's `.claude/skills/`. Only `uv tool install specify-cli` is meant to reach outside a project, and it lands in your user profile.

---

## Part A: Spec Kit

GitHub's Spec Kit ships a CLI (`specify`) and, for Claude Code, a set of skills prefixed `speckit-`. It enforces a five-step pipeline: constitution, specify, plan, tasks, implement. The same init also installs optional skills that sit alongside that pipeline: `/speckit-clarify` (ask the spec's open questions), `/speckit-analyze` (cross-check spec, plan and tasks), `/speckit-checklist` (generate a review checklist), `/speckit-converge` (append the unbuilt work to `tasks.md`) and `/speckit-taskstoissues`, which 1.2.1 deprecates in favor of the `github` extension.

### Setup: Install the Specify CLI

```bash
uv tool install specify-cli==1.2.1 --reinstall
specify version
```

`specify version` prints the CLI version, your Python version and your platform. It must read `1.2.1`: the version is what makes the command names below correct or stale.

> **This installs into your user profile.** `uv tool list` shows it, `uv tool uninstall specify-cli` removes it. `--reinstall` replaces whatever `specify-cli` the machine already carries; without it, `uv tool install` leaves an older version in place, and older releases name the commands with a dot (`/speckit.specify`) where 1.2.1 uses a hyphen. Note your previous version before you run this if you need to restore it.

If `uv` is not installed, follow [astral.sh/uv](https://docs.astral.sh/uv/) first. `pipx install --force specify-cli==1.2.1` pulls the same [PyPI package](https://pypi.org/project/specify-cli/) if you prefer pipx.

### Setup: Initialise the Project

The starter folder ships in this repo beside the solution reference, and the `.gitignore` it carries already lists `.specify/`, `.claude/` and `specs/`, so nothing the initialiser writes lands in the course repo. Change into it and run the initialiser there, from the root of your checkout:

```bash
cd labs/11-planning/02-tooling/notes-cli-speckit
cat .gitignore
specify init . --integration claude --script sh --force --non-interactive
```

All three commands work unchanged in PowerShell. `cat .gitignore` prints the ten ignore lines the starter ships; that is the whole starter before init runs.

`--non-interactive` stops init waiting for a keypress, and `--force` lets it merge into a folder that already holds the starter's `.gitignore`: without `--force` it exits with `Current directory is not empty and --non-interactive was set`. Never drop `--integration claude` from that line, because the non-interactive default integration is GitHub Copilot, which writes a `.github/` folder and no skills Claude Code can see.

> **Windows:** `--script sh` emits bash scripts under `.specify/scripts/bash/` and needs git-bash on PATH. If you work in plain PowerShell or `cmd`, use `--script ps` instead and the same scripts are generated as `.ps1`. `--integration claude` is the current flag; the `--ai claude` form from older releases is gone and exits with `No such option: --ai`.

`specify init` creates a `.specify/` directory (templates, scripts, workflows, and `memory/` for the constitution) plus the speckit skills under `.claude/skills/`. There is no top-level `memory/` folder and no `.claude/commands/` folder. The real tree:

```text
.specify/
  .gitignore
  init-options.json
  integration.json
  integrations/{claude,speckit}.manifest.json
  memory/{.constitution-template.json,constitution.md}
  scripts/bash/{check-prerequisites,common,create-new-feature,resolve-template,setup-plan,setup-tasks}.sh
  templates/{spec,plan,tasks,checklist,constitution}-template.md
  workflows/speckit/workflow.yml
  workflows/workflow-registry.json
.claude/skills/
  speckit-constitution/SKILL.md
  speckit-specify/SKILL.md
  speckit-plan/SKILL.md
  speckit-tasks/SKILL.md
  speckit-implement/SKILL.md
  speckit-clarify/  speckit-analyze/  speckit-checklist/
  speckit-converge/ speckit-taskstoissues/
```

Now start Claude Code in `notes-cli-speckit`, as the launch block above shows.

Confirm the commands are available by typing `/` and looking for `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`. The separator is a **hyphen** (older releases used a dot): the Claude Code integration installs skills, and the skill name is the command name. The CLI prints the same list in its own "Next steps" panel right after init.

> **Steps 1 to 5 need a live, interactive Claude Code session.** They are slash commands typed into a running `claude`.

---

### Step 1: Establish a Constitution

**Goal:** Lock the project's governing principles before any feature work. Spec Kit calls this the "constitution": it constrains every subsequent step.

**Prompt:**

```text
/speckit-constitution Principles for notes-cli: 1. Python stdlib only beyond Typer, no external runtime dependencies. 2. Storage is SQLite via sqlite3 stdlib, no ORM. 3. Every command must be testable in isolation; database state is the only contract. 4. Existing notes.db rows must keep working across schema changes, no destructive migrations. 5. CLI surface stays small: each new feature adds at most two new commands.
```

**Expected result:** Spec Kit fills in `.specify/memory/constitution.md` (init ships it as an unfilled template) with the five principles. Claude confirms the constitution is in place. From here on, every plan or task it generates references these constraints.

---

### Step 2: Specify the Feature

**Goal:** Produce a feature spec from a product-level description. Spec Kit's contract here is *what and why*; tech choices wait for `/speckit-plan`.

**Prompt:**

```text
/speckit-specify Add tag-based search and pinning to notes-cli. Users can attach one or more tags to a note, search notes by combinations of tags (with AND semantics across tags), and mark notes as pinned so they appear at the top of the list output. Existing notes without tags or pins must continue to work unchanged.
```

**Expected result:** Spec Kit creates a numbered feature folder (for example `specs/001-tag-based-search/`) containing a `spec.md` with sections for problem statement, user stories, acceptance criteria, and out-of-scope items. **Read it.** Compare against the constraints you wrote into `STATE.md` in Lab 01: Spec Kit's spec is more verbose, more user-facing, and silent on schema decisions (those come in `/speckit-plan`).

The numbering is done by a shell script, deterministically. You can watch it work without a Claude session:

```bash
bash .specify/scripts/bash/create-new-feature.sh --json "Add tag-based search and pinning to notes-cli"
```

It prints `{"BRANCH_NAME":"001-tag-based-search", ..., "FEATURE_NUM":"001"}` and seeds `specs/001-tag-based-search/spec.md` from the template. The scripts anchor on the `.specify/` marker directory, so they will not walk up into an enclosing git repository.

---

### Step 3: Generate the Plan

**Goal:** Add tech-stack and architecture choices on top of the feature spec.

**Prompt:**

```text
/speckit-plan Tech stack: Python 3.12, Typer, sqlite3 stdlib. Schema additions: normalised tags table and note_tags junction table, no JSON columns. Add a pinned column (INTEGER default 0) to the existing notes table. Multi-tag query uses GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = N. List ordering: pinned DESC, then id DESC. Migration runs idempotently on startup.
```

**Expected result:** Spec Kit writes `plan.md` in the same feature folder, expanding the spec into concrete technical sections: schema, query strategy, file changes, migration approach. Read it, then **compare against the Extended Thinking output from Lab 01 Step 3**. Note where Spec Kit's plan agrees, where it disagrees, and where it is silent.

---

### Step 4: Decompose Into Tasks

**Goal:** Turn the plan into an actionable task list.

**Prompt:**

```text
/speckit-tasks
```

**Expected result:** A `tasks.md` file with a numbered, ordered task list. Each task has a clear deliverable. Compare against the three work packages you built in Lab 01 Step 5: Spec Kit usually generates more, smaller tasks (often 8 to 15), each scoped to a single file change. The manual decomposition treated each *concern* as a unit; Spec Kit treats each *file edit* as a unit.

Optionally run `/speckit-analyze` here. It cross-checks the constitution, spec, plan and tasks against each other and reports contradictions before you spend tokens implementing them.

---

### Step 5: Execute and Compare Metrics

**Goal:** Run the implementation, then write a short comparison report into both `STATE.md` and the new spec folder.

**Prompt:**

```text
/speckit-implement
```

After the run finishes, ask Claude (no slash command needed):

```text
Write a comparison report to compare-vs-manual.md in this folder with the following sections:

  ## Tokens
  Approximate token cost of the Spec Kit run vs. the manual Lab 01 run. Run /cost inside the session (it is an alias for /usage) or estimate.

  ## Files generated
  List every file the spec-kit pipeline produced (.specify/, specs/<feature>/, source files).

  ## Decisions captured automatically
  Which decisions did Spec Kit force you to write down that you skipped when working by hand?

  ## Decisions skipped
  Which decisions did Spec Kit leave to the model that you handled explicitly in Lab 01?

  ## Verdict
  When would you reach for spec-kit vs. doing it by hand? Two sentences max.
```

**Expected result:** A `compare-vs-manual.md` file with the five sections filled in. The verdict typically lands on: *Spec Kit for unfamiliar domains where the constitution and spec pipeline forces discipline; by-hand Plan Mode for familiar domains where the overhead is not worth it.*

---

## Part B: BMAD-METHOD

BMAD ("Breakthrough Method for Agile AI Driven Development") takes a different shape: a roster of role-playing agents that you invoke in sequence, plus a "party mode" where they collaborate in one session. The `bmm` module installs six personas: PM (John), Architect (Winston), Developer (Amelia), UX Designer (Sally), Analyst (Mary) and Tech Writer (Paige). There is no QA persona; review work lives in task skills such as `bmad-code-review` and `bmad-review-edge-case-hunter`.

### Setup: Install BMAD

BMAD 6.x expects Node 18 or newer and `uv` (you installed it in Part A: BMAD workflows increasingly shell out to `uv run`). `npx` prompts to download `bmad-method` on first use, so pass `--yes` to `npx` as well in a non-interactive shell.

In a third fresh folder, again from the root of your checkout:

```bash
mkdir -p labs/11-planning/02-tooling/notes-cli-bmad
cd labs/11-planning/02-tooling/notes-cli-bmad
printf '.claude/\n_bmad/\n_bmad-output/\n' > .gitignore
npx --yes bmad-method install --directory . --modules bmm --tools claude-code --output-folder docs --yes
```

`--output-folder docs` is deliberate: without it BMAD writes planning artefacts to `_bmad-output/planning-artifacts` and treats `docs/` as read-only project knowledge, and the paths in Step 6 will not match what the agents produce.

The install writes its module content into `_bmad/`, creates the output folders for generated artefacts, and registers 46 skills into `.claude/skills/`. Its summary panel prints `claude-code (46 skills -> .claude/skills)`. There is no `.bmad/` directory anywhere. The real top level after install:

```text
_bmad/            _config, bmm, core, custom, scripts, config.toml, config.user.toml
docs/             output folder (planning and implementation artefacts)
.claude/skills/   46 bmad-* skills, including the six bmad-agent-* personas
```

> **Undo:** everything BMAD writes is inside this folder. Deleting `_bmad/`, `.claude/skills/bmad-*` and the output folder removes it completely; nothing is installed into your user profile. `npx` itself caches the package under your npm cache, which `npm cache clean --force` clears.

Part B runs in its own project, so start a second Claude Code session here, in `notes-cli-bmad`:

```bash
claude
```

> **Steps 6 and 7 need a live, interactive Claude Code session.**

Confirm the install by asking Claude:

```text
/bmad-help What's the entry point for a new feature?
```

`bmad-help` is BMAD's built-in skill: it reads your current state and tells you which skill to invoke next.

---

### Step 6: Walk the BMAD Pipeline

**Goal:** Run the same tag-and-pin feature through BMAD's PM, Architect and Developer flow. Do not implement; capture artefacts only.

**Prompt:**

Follow `bmad-help`'s guidance. The typical flow is:

```text
Invoke the PM agent (bmad-agent-pm, "John") and have it produce a PRD for the same feature: tag-based search and pinning on notes-cli, AND semantics across tags, pinned notes sort first. Save the PRD as prd.md in the configured output folder.

Then invoke the Architect agent (bmad-agent-architect, "Winston") and have it produce an architecture document covering: schema additions, migration strategy, query approach. Save it as architecture.md beside the PRD.

Then invoke the Developer agent (bmad-agent-dev, "Amelia") and have it produce story files, one per implementable unit, in a stories/ folder beside the PRD. Each story should be small enough that a single Claude session can complete it.

Stop before implementation. Do not write source code.
```

The document-producing work is also reachable directly as skills: `bmad-prd`, `bmad-architecture`, `bmad-create-epics-and-stories` and `bmad-create-story`. The older `bmad-create-prd` and `bmad-create-architecture` skills still exist but are deprecated shims that forward to the consolidated ones.

**Expected result:** Three artefact sets in your configured output folder: a PRD, an architecture document, and a folder of story files. If you skipped `--output-folder docs` at install time, look under `_bmad-output/planning-artifacts/` instead. Notice the verbosity difference: BMAD's PRD is several pages, written for human stakeholders; Spec Kit's `spec.md` is half that length, written for an agent.

For the contrast, try `/bmad-party-mode` afterwards and put the same feature in front of several personas at once.

---

### Step 7: Side-by-Side Verdict

**Goal:** Write a short verdict comparing all three approaches.

**Prompt:**

```text
Write side-by-side-verdict.md at the root of this folder with these sections:

  ## When to reach for each
  - Plan Mode by hand (Lab 01): [one sentence]
  - Spec Kit (Part A): [one sentence]
  - BMAD-METHOD (Part B): [one sentence]

  ## Where the overlap is real
  [What do all three force you to do that you'd otherwise skip?]

  ## Where the overhead bites
  [Which of the three would feel like ceremony on a one-hour feature?]

  ## My default
  [Which one would you reach for first on the next non-trivial feature? Why?]
```

**Expected result:** A short, opinionated `side-by-side-verdict.md`. The "my default" section usually lands on Plan Mode for small features, Spec Kit for unfamiliar domains where the constitution discipline pays off, and BMAD when the *output artefacts themselves* need to be readable by non-engineering stakeholders (PMs, designers).

---

## What You Just Practised

| Concept | Lab 01 (manual) | Part A (Spec Kit) | Part B (BMAD) |
|---|---|---|---|
| Governing principles | implicit in CLAUDE.md | `/speckit-constitution` | PM agent's PRD section |
| Feature spec | `STATE.md` Decisions section | `/speckit-specify` produces `spec.md` | PRD via `bmad-agent-pm` (John) |
| Technical plan | Plan Mode iteration and Extended Thinking | `/speckit-plan` produces `plan.md` | architecture via `bmad-agent-architect` (Winston) |
| Task decomposition | three work packages | `/speckit-tasks` produces `tasks.md` | story files via `bmad-agent-dev` (Amelia) |
| Execution | Plan Mode off, run packages | `/speckit-implement` | manual per story |
| Verification | self-critique against Done Criteria | `/speckit-analyze` and `/speckit-checklist` | review skills (`bmad-code-review`, `bmad-review-edge-case-hunter`) |
| Install footprint | none | 10 skills in `.claude/skills/`, plus a user-profile CLI | 46 skills in `.claude/skills/`, plus `_bmad/` |

The point is not that one is better. You can now read a spec, plan, or story file in any project and recognise which tradition it belongs to, and reach for the right tool for the size of the work in front of you.
