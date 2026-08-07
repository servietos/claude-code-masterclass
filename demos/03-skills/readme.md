# Module 3: Creating & Managing Skills

- Skills vs. slash commands
- Invocation model, anatomy, and body structure
- Choosing the skill by failure mode
- Manual authoring and conversation extraction
- Front matter fields
- Allowed-tools restrictions and metadata conventions
- Composite skills: scripts, references, and assets
- Cross-skill references and delegation patterns
- Dynamic context injection with `` !`command` ``
- Forked execution with `context: fork`
- Readiness, distribution, hosting, packaging
- Positioning a skill as an outcome
- Measurement: baselines, triggers, eval loop
- Diagnosis: symptom to `SKILL.md` layer

## Topics

| Topic | Description |
|-------|-------------|
| [01: Intro](01-intro/readme.md) | Skills vs. slash commands side-by-side: location, invocation, YAML frontmatter anatomy, body structure, and when to choose each approach. |
| [02: Creating](02-creating/readme.md) | The `SKILL.md` file itself: directory placement, the full frontmatter field reference, body structure, argument substitutions, and extracting a proven conversational workflow. |
| [03: Composite](03-composite/readme.md) | Bundling `scripts/`, `references/`, and `assets/` into one portable folder: progressive disclosure, reference files versus playbooks, stacking, precedence, and cross-skill delegation. |
| [04: Live Data and Subagents](04-live-data-and-subagents/readme.md) | Injecting live command output into a skill prompt with `` !`command` ``, and running a skill in an isolated subagent with `context: fork`, `agent`, and `background`. |
| [05: Test and Package](05-test-and-package/readme.md) | Getting a working skill into someone else's hands: the functional readiness gate, distribution as a portable folder, the skills API, hosting, packaging, and positioning. |

## Demos

Each runnable folder inside a topic is the starter and stays pristine. Its completed counterpart sits beside it as `<starter>-solution/`, where installs, lockfiles and runs happen. Every demo guide names its solution folder once as the finished reference and otherwise walks you through the starter.

| Topic | Description |
|-------|-------------|
| [02: Creating](02-creating/demo-skill-from-conversation.md) | Prompts Claude to build a JavaScript sales-revenue calculator, then encodes the proven interaction pattern into a reusable skill. |
| [04: Live Data and Subagents](04-live-data-and-subagents/demo-live-context-and-fork.md) | Inlines a project's file listing and open TODO markers with `` !`command` ``, then forks the same evidence to an Explore subagent and compares what each leaves in context. |
| [05: Test and Package](05-test-and-package/demo-test-and-package-a-skill.md) | Builds a trigger and functional test matrix for the `code-reviewer` skill, patches the failures it exposes, and packages the result as an installable folder. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Labs

| Lab | Description |
|-----|-------------|
| [Package Invoice Generation Into a Skill Claude Fires on Its Own](../../labs/03-skills/lab-01-invoice-docx-skill.md) | Build a composite `invoice-docx` skill: triggering frontmatter, restricted `allowed-tools`, a layout contract in `references/`, and docx-js rendering. |
| [Serve the Same Document Generator to Clients That Are Not Claude](../../labs/03-skills/lab-02-invoice-document-api.md) | Refactor the renderer so one module serves both the CLI and an HTTP endpoint returning real `.docx` bytes. |

## Knowledge Check

### CQ-01: Why Progressive Disclosure Matters

A team ships fifteen skills, each with a 400-line `SKILL.md`. A colleague worries this will exhaust the context window before any work starts. What actually loads?

- A) All fifteen `SKILL.md` bodies, which is why skill count has to be kept low.
- B) Only the YAML frontmatter of each skill; the body loads when the skill becomes relevant, and linked reference files load after that.
- C) Nothing until a skill is invoked by name with a slash command.
- D) The frontmatter plus the first heading of each body, as a preview for the routing decision.

**Answer: B**

Skills use progressive disclosure. The `name` and `description` in frontmatter are always loaded so the model can decide relevance; the body loads only when the skill is selected, and files it links to load only when needed. That is what makes a large skill library affordable, and it is also why a skill with no description can never be chosen.

### CQ-02: A Skill or a Slash Command

A team wants Terraform conventions available to Claude, but only when it is actually working on infrastructure code, without cluttering context the rest of the time. Which mechanism fits?

- A) A `CLAUDE.md` inside the `infrastructure/` directory holding the guidelines.
- B) A skill at `.claude/skills/terraform-conventions/SKILL.md` whose description names Terraform work.
- C) A slash command that the developer types before starting infrastructure work.
- D) A subagent restricted to the `infrastructure/` path with the conventions in its system prompt.

**Answer: B**

A skill is the mechanism designed for conditional, intent-triggered domain knowledge: the description is always visible so the model can route to it, and the body costs nothing until it does. Option A loads unconditionally for anything under that directory and misses Terraform files elsewhere. Option C works but depends on the developer remembering, which is what the trigger description exists to avoid.

### CQ-03: What Makes a Skill Discoverable

A skill exists, is well written, and is never selected. Which defect explains that most often?

- A) The `SKILL.md` body is too long, so the router skips it.
- B) The frontmatter `description` is missing, generic, or carries no concrete trigger phrases.
- C) The skill folder is not listed in `settings.json`.
- D) The skill has no `allowed-tools` entry, so the harness treats it as inert.

**Answer: B**

Skills surface to the model by their description, so that one field decides whether the skill is ever considered. A description that carries concrete trigger phrases matching how people actually phrase the request is the difference between a skill that fires and one that sits unused. Body length affects cost after selection, not selection itself.

### CQ-04: Keeping a Master Skill Discoverable

A large skill is split into a router plus six leaf documents. How should the leaves be structured?

- A) Each leaf gets its own `SKILL.md` with frontmatter, nested inside the master skill's folder.
- B) Each leaf is a plain `references/<leaf>.md` with no frontmatter, and the router tells the model to read the matching file.
- C) Each leaf is promoted to a top-level skill and the router lists them by name for the model to invoke.
- D) All six leaves are concatenated into the router's body under separate headings.

**Answer: B**

A master skill holds exactly one `SKILL.md` at its root and delegates by instructing the model to read `references/<leaf>.md`. Frontmatter is what causes a file to be discovered as a skill, so leaves must not carry it, and a nested `SKILL.md` creates a second discoverable skill inside the first. Option D throws away the progressive disclosure that made the split worthwhile.

### CCA-F Q46 (Domain 3: Claude Code Configuration and Workflow)

A development team wants to provide Claude Code with a specialized set of instructions for writing and refactoring Terraform configurations. These instructions should only be activated when Claude is working on relevant tasks to avoid cluttering its context unnecessarily. According to Anthropic's official documentation, what is the recommended approach to implement this conditional context?

- A) Place a `CLAUDE.md` file directly inside the `infrastructure/` directory with the Terraform-specific guidelines.
- B) Create a new "Skill" by adding a directory like `.claude/skills/terraform-best-practices/` and placing the guidelines within a `SKILL.md` file inside it.
- C) In the `.claude/config.json` file, define a new agent profile that maps the Terraform guidelines to the `infrastructure/` path.
- D) Add the Terraform guidelines to a root `.claude/instructions.md` file and use YAML frontmatter to specify the path: `paths: ["infrastructure/"]`.

**Answer: B**

Anthropic's official documentation defines Skills as folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Each skill is self-contained in its own folder with a SKILL.md file. Claude uses progressive disclosure: the YAML frontmatter is always loaded, the SKILL.md body is loaded only when the skill is relevant, and linked files are loaded as needed.
