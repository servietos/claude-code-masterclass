# Module 2: Claude Code Configure Harness

- Settings hierarchy and CLAUDE.md injection
- CLAUDE.md constitution and `@`-file mentions
- Built-in and custom slash commands
- MCP transports and `.mcp.json` configuration
- Installable skills: folders and sources
- Sub-agents under `.claude/agents/`
- Hooks: PreToolUse, PostToolUse, Stop
- Mods: extend and customize the harness
- Auto-memory: `MEMORY.md` index and files

## Topics

| Topic | Description |
|-------|-------------|
| [01: Intro Constitution](01-intro-constitution/readme.md) | Harness overview, settings hierarchy (global, project, session), and how `CLAUDE.md` injects rules and context into every turn; context engineering with the multi-layer `CLAUDE.md` hierarchy (global, project, subfolder), `@`-file mentions, and examples that pin the output shape. |
| [02: Commands](02-commands/readme.md) | Built-in and custom slash commands, argument patterns, and authoring reusable workflows under `.claude/commands/`. |
| [03: MCP](03-mcp/readme.md) | Model Context Protocol servers (stdio, HTTP, WebSocket), `.mcp.json` configuration, and developer use cases like Playwright, Azure Deploy, GitHub, and Microsoft Learn. |
| [04: Skills](04-skills/readme.md) | What a skill folder is and where skills come from: the catalog, `/find-skills`, and what an install actually changes. [Module 3](../03-skills/readme.md) owns anatomy, frontmatter, and forked execution. |
| [05: Subagents](05-subagents/readme.md) | Sub-agents as a harness file type under `.claude/agents/`, discovered alongside commands, hooks, and skills. [Module 6](../06-subagents/readme.md) owns frontmatter, orchestration, and contracts. |
| [06: Hooks and Mods](06-hooks-mods/readme.md) | Event-driven shell hooks for `PreToolUse`, `PostToolUse`, `Notification`, and `Stop`, wired in `settings.json` and proven through the exit-code contract, and mods that extend and customize the harness itself: they watch or rewrite any event, hold a tool call for a person, and add panes, bands, and commands. [Module 9: 02](../09-observability/02-guardrails/readme.md) owns destructive-command guardrails. |
| [07: Memory](07-memory/readme.md) | The auto-memory system: the `MEMORY.md` index and the `user`, `feedback`, `project`, and `reference` file types. [Module 8: 04](../08-optimize/04-memory-architectures/readme.md) benchmarks whole memory architectures. |

## Demos

| Topic | Description |
|-------|-------------|
| [01: Intro Constitution](01-intro-constitution/demo-claude-md-constitution.md) | Builds a three-layer CLAUDE.md (global, project, subfolder) from a real project map, then replaces pasted code with `@`-mentions and separates durable rules from `/memory` notes. |
| [02: Commands](02-commands/demo-slash-command-toolkit.md) | Turns a dependency-free changelog CLI into a four-command toolkit, covering frontmatter fields, zero-based positional arguments, the `` !`command` `` bash injection, and project versus personal command scope. |
| [03: MCP](03-mcp/demo-maf-foundry-migration.md) | Connects the Microsoft Agent Framework starter to a live Azure AI Foundry project and migrates it to the current API using Microsoft Learn MCP lookups. |
| [04: Skills](04-skills/demo-docx-invoice.md) | Installs a DOCX skill and uses it to generate a TypeScript program that renders a sample invoice as a `.docx` file. |
| [06: Hooks and Mods](06-hooks-mods/demo-hook-pipeline.md) | Builds a `PreToolUse`, `PostToolUse`, and `Stop` pipeline in stdlib Python, teaching the `settings.json` wiring shape, the stdin payload contract, and the exit-code semantics with 15 passing tests. |
| [06: Hooks and Mods](06-hooks-mods/demo-skill-guard.md) | Guards the master-skill folder convention with two hooks: a `PreToolUse` blocker that refuses a nested `SKILL.md` before it lands, and a `PostToolUse` bash linter that sweeps `.claude/skills/` and `.claude/agents/` for defects the blocker cannot see. |
| [06: Hooks and Mods](06-hooks-mods/demo-cache-meter.md) | Installs a prompt-cache meter mod from a template gallery, reviews what it can reach with `claude plugin validate` and its tests, watches a model switch rewrite the cache in its `/cache` pane, and pins its options under the full plugin id in a `--settings` file. |
| [06: Hooks and Mods](06-hooks-mods/demo-intent-guard.md) | Loads a guard mod with `--plugin-dir` that holds a destructive git command you never asked for and passes it once a prompt asks for its effect, then adds a package-publish family with two tests. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Labs

| Lab | Description |
|-----|-------------|
| [Install a React Agent Skill](../../labs/02-harness/lab-01-react-skill.md) | Install the `react-best-practices` skill into the React app's own `.claude/skills/` and confirm it is active. |
| [Configure the Harness on a Broken React App](../../labs/02-harness/lab-02-fix-the-react-food-shop.md) | Configure the harness piece by piece, then watch it work together as Claude fixes a broken React app. |
| [Apply Prompting Techniques](../../labs/02-harness/lab-03-prompting-techniques.md) | Apply five prompting techniques to your harness: statefile maintenance, anchors, `@`-mentions, few-shot examples, and slash-command promotion. |
| [Build an Ask-Check Mod Test-First](../../labs/02-harness/lab-04-ask-check.md) | Build a mod that shows your own earlier answer above the prompt when Claude asks again, test-first against six shipped tests. |

## Knowledge Check

### CQ-01: Unconditional Context Versus Scoped Rules

A team has one convention that applies to the whole repository (commit message format) and one that applies only to files matching `*.migration.ts` wherever they sit in the tree. Where does each belong?

- A) Both in the root `CLAUDE.md`, with a sentence telling Claude to check the filename before applying the second.
- B) Commit format in the root `CLAUDE.md`; the migration convention in `.claude/rules/migrations.md` with `paths: ["**/*.migration.ts"]`.
- C) Both in `.claude/rules/`, since rules are the newer mechanism and supersede `CLAUDE.md`.
- D) Commit format in `settings.json` under a conventions key; the migration convention in a nested `CLAUDE.md`.

**Answer: B**

`CLAUDE.md` is unconditional and right for anything that applies everywhere. A rule file with `paths:` frontmatter loads only when Claude touches a matching file, which is what a pattern-scoped convention needs. Option A works but pays the context cost on every turn and depends on the model checking a filename, and option D puts prose in a file that holds settings.

### CQ-02: A Hook or a Prompt Instruction

An organization must guarantee that no agent writes to a path outside `src/`, with no exceptions. Which mechanism provides the guarantee?

- A) A `CLAUDE.md` rule stating the constraint in strong language, repeated at the top and bottom of the file.
- B) A `PreToolUse` hook that inspects the target path and blocks the call before it executes.
- C) A `PostToolUse` hook that reverts any write landing outside `src/`.
- D) A subagent whose sole job is to review every write the main agent proposes.

**Answer: B**

Only a `PreToolUse` hook is deterministic: it runs outside the model's reasoning and blocks the call before anything happens. Prompt instructions are probabilistic and will eventually be missed. A `PostToolUse` hook detects the violation after the write already occurred, which is auditing rather than prevention, and option D puts another stochastic component in the enforcement path.

### CQ-03: Why the Junior Developer Gets Different Behavior

A senior developer configured custom build commands and they work perfectly on their machine. A colleague clones the same repo and Claude Code invents standard build commands instead. What is the most likely cause?

- A) The colleague needs to run `/doctor` to rebuild the local harness index after cloning.
- B) The configuration lives in the senior developer's `~/.claude/`, so it was never committed and does not travel with the repo.
- C) The colleague's CLI version predates the configuration format used.
- D) The repo `CLAUDE.md` is missing an import for the colleague's operating system.

**Answer: B**

Harness files resolve from the current directory upward and finally from the user's home directory. Anything placed in `~/.claude/` is personal, never enters a pull request, and cannot reach a teammate. Configuration a team depends on belongs in the repo's `.claude/`, committed like any other shared asset.

### CQ-04: Isolating Context in a Monorepo

A monorepo holds several microservices, each with its own testing framework and fixture conventions. Claude keeps hallucinating Service A's fixtures when writing tests for Service B. What resolves this with the least machinery?

- A) A `CLAUDE.md` at each microservice root, since Claude resolves context from the nearest file in the directory tree.
- B) One root `CLAUDE.md` with conditional markdown blocks per service, selected by a CI flag.
- C) A separate JSON file of fixture definitions per service, pointed at by a context directory flag.
- D) A subagent per microservice, each with the fixture conventions in its system prompt.

**Answer: A**

`CLAUDE.md` files resolve from the working directory upward and merge, so a file at each service root gives that service its own conventions without leaking into its siblings. It requires no flags, no scripts, and no CI wiring. Option D would work but adds an agent layer to solve a context-scoping problem.

### CQ-05: What an Administrator Can Actually Enforce

A platform team must guarantee that no developer can enable an unapproved MCP server, on any machine, in any repo. Which approach delivers that?

- A) A committed `.claude/settings.json` in every company repository listing the approved servers.
- B) An onboarding script that appends the approved list to each developer's `~/.claude/settings.json`.
- C) A managed settings file deployed through MDM or OS policy, using `allowedMcpServers`.
- D) A `CLAUDE.md` entry instructing Claude to refuse connections to unlisted servers.

**Answer: C**

Managed settings sit above project, user, and local scopes and cannot be overridden, which is what turns a preference into a control. `allowedMcpServers` and `deniedMcpServers` restrict which servers may load at all. Options A and B are both editable by the developer they are meant to constrain, and option D asks the model to enforce a policy about its own configuration.

### CCA-F Q10 (Domain 1: Agentic Architecture and Orchestration)

A network security agent uses an `update_firewall` tool that accepts `allow_ip` and `block_ip` arrays. Security policy dictates that an IP address cannot exist in both arrays simultaneously, and the `0.0.0.0/0` CIDR can only be added if an `override_admin` flag is set to true. The model occasionally violates these complex cross-argument rules. How can you guarantee 100% compliance with this policy?

- A) Add a negative constraint to the system prompt, explicitly forbidding the model from putting the same IP in both lists. The prompt should also state that using `0.0.0.0/0` requires the `override_admin` flag.
- B) Implement a PreToolCall hook that validates arguments against the security policy, blocking the tool call and returning a specific error to the model if any rules are violated.
- C) Modify the backend firewall API to validate the `allow_ip` and `block_ip` arrays upon receipt. The API would silently drop any IP in both lists or `0.0.0.0/0` if the override flag is missing.
- D) Implement a PostToolUse hook that audits the firewall rules after the tool executes. It would check for IPs in both lists or an invalid `0.0.0.0/0` entry, then alert an administrator of the violation.

**Answer: B**

A PreToolCall hook provides a deterministic layer of protection by intercepting the tool call before it reaches the execution environment. By validating the argument set against the security policy, the system can block invalid requests and return structured validation errors, allowing the model to correct itself while ensuring 100% compliance.

### CCA-F Q44 (Domain 3: Claude Code Configuration and Workflow)

An enterprise maintains a monorepo containing multiple microservices. Each microservice uses entirely different testing frameworks and fixture conventions. A single CI pipeline runs Claude Code to generate unit tests for whichever microservice was modified in a given pull request. Currently, Claude Code frequently hallucinates fixtures from Service A when generating tests for Service B. How should the architect resolve this context confusion in the CI pipeline without writing complex dynamic prompt injection scripts?

- A) Place a distinct CLAUDE.md file in the root directory of each microservice detailing its specific testing standards; Claude Code will automatically resolve context based on the nearest CLAUDE.md in the directory tree.
- B) Create a global CLAUDE.md file at the root of the monorepo that uses conditional markdown blocks to specify which fixtures belong to which service, and configure the CI pipeline to pass the --custom-instructions flag pointing to this file.
- C) Configure the CI pipeline to pass the --isolate-context flag, which forces Claude Code to ignore all files outside the immediate working directory, and rely on a per-service CLAUDE.md for fixture guidance.
- D) Use the --context-dir flag in the CI pipeline to point Claude Code to a centralized repository of JSON-formatted fixture definitions, and maintain a separate JSON file per microservice with its own fixture schemas.

**Answer: A**

Claude Code automatically resolves context based on the nearest CLAUDE.md in the directory tree. Placing a distinct CLAUDE.md in each microservice's root allows each service to define its own testing frameworks and fixture conventions without leaking context to other services.

### CCA-F Q45 (Domain 3: Claude Code Configuration and Workflow)

Your enterprise application has a strict separation between public APIs and internal APIs. Public API routes are always named `*public.route.ts` and internal API routes are named `*internal.route.ts`, scattered across dozens of domain folders. You need Claude to apply strict rate-limiting conventions ONLY when editing public API routes. What is the most precise way to configure this?

- A) Create .claude/rules/rate-limiting.md with YAML frontmatter paths: ["**/public/**/*.ts"].
- B) Add the rate-limiting conventions to the root CLAUDE.md and instruct Claude to check the filename before applying them.
- C) Create .claude/rules/rate-limiting.md with YAML frontmatter paths: ["**/*public.route.ts"].
- D) Create a CLAUDE.md file in every domain folder and use YAML frontmatter exclude: ["*internal.route.ts"].

**Answer: C**

This option precisely targets all files ending with public.route.ts using a glob pattern in the YAML frontmatter. This ensures the rate-limiting conventions are loaded only when editing files that match the public API naming convention, regardless of which domain folder they reside in.

### CCA-F Q50 (Domain 3: Claude Code Configuration and Workflow)

A financial institution's monorepo contains three distinct applications: `apps/retail`, `apps/corporate`, and `apps/internal`. The `retail` and `corporate` apps must adhere to strict PCI-DSS logging compliance, while the `internal` app does not. The architect wants to enforce this compliance for all TypeScript files in the regulated apps without polluting the context window when developers work on the internal app. Which configuration is most precise?

- A) Create `.claude/rules/pci-logging.md` with `paths: ["apps/retail/**/*.ts", "apps/corporate/**/*.ts"]`.
- B) Place a `CLAUDE.md` in the root directory with `exclude: ["apps/internal/**/*.ts"]`.
- C) Create a `.claudeignore` file in `apps/internal` containing the entry `!pci-logging.md`.
- D) Create `.claude/rules/pci-logging.md` with `paths: ["apps/**/*.ts"]` and add a markdown instruction to ignore the internal app.

**Answer: A**

Claude Code rules are defined in Markdown files within the .claude/rules/ directory. The paths frontmatter within a rule file is the official and most precise mechanism for scoping the rule's application to specific files and directories.

### CCA-F Q53 (Domain 3: Claude Code Configuration and Workflow)

A senior developer sets up Claude Code for a new microservices project, configuring custom build commands and linting rules. When a junior developer clones the repository and runs Claude Code, the agent hallucinates standard build commands instead of using the custom ones. The senior developer's environment works perfectly. What is the most likely cause of this discrepancy?

- A) The junior developer needs to run /memory load to fetch the project-level configuration from the remote repository.
- B) The junior developer's Claude Code CLI version is incompatible with the .claude/rules/ directory structure.
- C) The project root CLAUDE.md is missing an @import statement for the junior developer's specific OS environment.
- D) The senior developer placed the configuration in ~/.claude/CLAUDE.md instead of the project-level .claude/CLAUDE.md.

**Answer: D**

Claude Code looks for configuration files in a specific hierarchy: first in the current directory, then in parent directories, and finally in the user's home directory. If the senior developer placed the custom commands in their global home directory config, those changes were never committed to the repository.

### CCA-F Q55 (Domain 3: Claude Code Configuration and Workflow)

A lead engineer wants to ensure that all new hires automatically have Claude Code configured to use the company's proprietary internal package registry. The solution must be centrally managed and require no manual configuration on the new hires' machines. Which approach aligns with Anthropic's recommended practices for enterprise environments?

- A) Commit a `.claude/settings.json` file containing the registry configuration to the root of every company repository.
- B) Provide a centrally managed onboarding script that appends the registry configuration to each new hire's user-specific `~/.claude/settings.json` file.
- C) Add the registry configuration to a `CLAUDE.md` file and use a server-managed setting to push this file, which requires a custom client-side plugin.
- D) Use a central management tool (MDM) or OS-level policies to deploy a managed settings file or apply the configuration directly, for example, via Windows Registry keys.

**Answer: D**

Claude Code supports managed settings for centralized enterprise control via file-based settings in system directories or MDM/OS-level policies, such as Windows Registry keys under `HKLM\SOFTWARE\Policies\ClaudeCode`. This enforces the configuration for all users on a machine without manual setup.

### CCA-F Q58 (Domain 3: Claude Code Configuration and Workflow)

A developer is integrating the `claude-code` command-line tool into a CI/CD pipeline. A step in the pipeline successfully generates a new Python module. The subsequent step, intended to perform a security analysis on the generated code, fails to produce a security report and instead returns a generic conversational response. The developer's script issued the prompt: "Review the new module for security vulnerabilities." What is the most likely reason the dedicated security analysis was not performed?

- A) The CI/CD runner lacks the necessary sandboxing configuration, a mandatory prerequisite that prevents the tool from activating its specialized security analysis mode.
- B) The developer used a generic prompt, but the tool's specialized security analysis is only activated by using the required `/security-review` slash command.
- C) The `--security-scan` flag was omitted from the `claude-code` command, causing the tool to default to a standard conversational response.
- D) The pipeline is using a base Claude model via an API, which does not support the specialized commands integrated into the full `claude-code` tool.

**Answer: B**

Claude Code's specialized security analysis is activated by the dedicated /security-review slash command. A generic prompt will not trigger the comprehensive, targeted security review that the slash command provides.
