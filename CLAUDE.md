# CLAUDE.md

Masterclass repo: **Agentic Software Engineering with Claude Code**. 14 sequential modules, mostly teaching markdown, a few runnable projects.

## Layout

- `demos/01-` … `demos/14-` = modules. Number = learning order. Never reorder.
- Module root: `readme.md` (indexes its demos in a `| Topic | Description |` table), numbered topic folders, `lab-NN-<slug>.md` guides, `pptx/`.
- Topic folder owns: `readme.md` (theory), `demo-<slug>.md`, `demo-presenter-<slug>.md`, its runnable starter.
- Starter stays pristine: no deps, no lockfile, no build output. Finished copy beside it as `<starter>-solution/`. Install and run in the solution only.
- Topics in one module own disjoint material. New topic: re-read siblings, delete what moved.
- Deck: `pptx/module-NN.yaml` + `module-NN.pptx`, rendered by the generator in `.claude/skills/create-module-pptx/build/`.
- A demo's finished skill lives at `.claude/skills/<name>/`, never in a demo or solution folder. Anchor paths with `${CLAUDE_PROJECT_DIR}`.
- `src/` = standalone runnable projects referenced by modules.

## Rules

- Never commit or push unless told in that message. Never delete files unless asked. Never handle or propose git issues unless asked.
- No unrequested content: no extra table, section, framing paragraph, takeaway. A rewrite is re-derived from the request, never from the previous draft.
- No em dashes. Relative internal links, `#anchors`. Every code fence declares a language.
- Quality check fails: fix the cause. Never `--no-verify`.
- Code carries no comments. Exception: `.sh`, `.ps1` and hooks under `demos/` get one short comment above each line a reader cannot decode (regex, exit codes, shell machinery, derived values, outcome-changing flags). Guide quotes match the file byte for byte.
- No error handling in scripts unless asked.
- Plan mode for 3+ steps or architectural work. Going sideways: stop and re-plan.
- Verify before done: run it, show the evidence. Minimal diff, simplest change that works.
- Checker is suspect, not witness. Open the file at the reported line. Confirm the defect is real before reporting. Never report an unreproduced finding. Never report a no-effect finding: fix it silently or drop it. A false positive means the checker measured the wrong thing: a link inside a code fence belongs to the quoted file, a CRLF-normalizing harness tests a phantom file.
- Never re-read files just written, never echo large blocks, batch edits.
- After a user correction: record the pattern in `tasks/lessons.md`.

## Skills own the detail

- **Authoring gate.** Before writing or editing any demo, presenter or lab guide, read `~/.claude/skills/create-class/references/create-guide.md`. It owns Setup rules, self-contained starters, shell-parity twins, intro separator, and the `diff` of starter against solution.
- **brand-voice-code** after any `demos/` readme edit. Rules in `.claude/skills/brand-voice-code/references/rules.md`.
- **mermaid-expert** before writing, editing or reviewing any Mermaid block. Verify by rendering, not by regex.
- **create-module-pptx** for decks. **class-dashboard** for module status.
- Browser work: `mcp__chrome-devtools__*` only. Playwright only when devtools is unavailable.

## Harness and delegation

Route domain work to the owning expert. Default, not fallback. Parallelize independent subtasks in one message. Subagents keep the main context clean.

| Task                                          | Agent                 |
| --------------------------------------------- | --------------------- |
| Angular components / services / state         | `angular-expert`      |
| .NET API / EF Core / migrations               | `dotnet-expert`       |
| SSH deploy to Ubuntu, GitHub Actions          | `github-devops-agent` |
| QA, screenshots, Lighthouse (only on request) | `playwright-expert`   |

Parallel review team for `demos/07-agent-teams/02-parallel-review`, one lens each, read-only:

| Lens                                          | Agent                       |
| --------------------------------------------- | --------------------------- |
| Auth, input validation, secrets, anon reach    | `review-security-agent`     |
| Query shape, tracking, un-awaited tasks        | `review-performance-agent`  |
| Existing coverage, what a first test asserts   | `review-tests-agent`        |

Every agent definition carries behaviors, a strict delegation table into its skill's reference leaves, and rules. Code patterns live in the skill, never in the agent: a pattern written from memory instead of read from the leaf is the defect the tables exist to prevent.

Repo-local commands in `.claude/commands/`: `/create-teaching` (enrich a module readme), `/create-lab` (scaffold a lab guide), `/scaffold-module-folders` (create topic folders).

## Skills (`.claude/skills/`)

<!-- SKILLS:BEGIN -->

Synced from the global library (`~/.claude/skills`) — 10:

- **angular-conventions** — Consolidated Angular conventions for components, dependency injection, forms, HTTP, routing, signals, MSAL
- **azure** — One Azure skill covering CLI conventions, GitHub Actions OIDC and Azure DevOps WIF, Bicep app registrations, Static Web Apps / App Service / Container Apps / ACR deploys, Azure SQL provisioning with Managed Identity auth, EF Core migration and .bacpac publish, PostgreSQL Entra passwordless auth, and customer-tenant administration
- **code-reviewer** — Review code. It supports both local changes (staged or working tree) and remote Pull Requests (by ID or URL)
- **compliance** — Compliance assessment routed to leaves: EU AI Act risk tiers and Article 50 transparency, DSGVO / GDPR personal data, accessibility (EAA, WCAG 2.1 AA)
- **dotnet-conventions** — .NET/C# coding conventions for ASP.NET Core controllers, EF Core models and migrations, unit testing
- **hook-caveman-compression** — Install, tune or remove the `UserPromptSubmit` hook that puts each turn in caveman mode, with the exclusion list that keeps finished prose untouched
- **mermaid-expert** — Mermaid diagram syntax and styling for every diagram type, verified by rendering
- **microsoft-agent-framework** — Microsoft Agent Framework (Python) development
- **track-time** — Customer-billable work log of AI machine hours for a git repo, appended to `.time/working-time.md`, with a billing-sheet leaf
- **ui-ux-pro-max** — UI/UX design intelligence: searchable database of styles, palettes, font pairings, UX guidelines and chart types across 22 stacks

Project-specific, kept only in this repo — 4:

- **agentic-seo** — SEO auditing, optimization, and Core Web Vitals tracking on any web project
- **brand-voice-code** — Audit and fix Markdown files for brand-voice quality in the Claude Code class (developer audience): em dashes
- **class-dashboard** — Evaluate module completeness and render the static progress dashboard in `dashboard/`; ships its own `templates/dashboard/` copies of the evaluator, renderer, web app and Pages workflow
- **create-module-pptx** — Distil a module's topic readmes and presenter guides into an essentials-only deck, written as generator YAML in that module's `pptx/` folder and rendered to `.pptx` by the generator the skill bundles in its own `build/`

Demo harness skills, the finished reference for a demo guide — 3:

- **data-aggregator** — Result of `demos/03-skills/02-creating/demo-skill-from-conversation.md`
- **my-order-brief** — Dynamic context injection, from `demos/03-skills/04-live-data-and-subagents/demo-live-context-and-fork.md`
- **my-order-audit** — The same evidence forked to an Explore subagent, from the same demo
<!-- SKILLS:END -->
