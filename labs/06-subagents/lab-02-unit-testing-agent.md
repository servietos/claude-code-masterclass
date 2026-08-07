# Build a scoped unit-testing agent with minimal permissions

Build a unit-testing sub-agent by first reasoning through the stack, permission model, and mocking rules in conversation with Claude, then applying a ready-made recipe or your own findings to implement it.

Each step follows the same pattern:

- **Goal** - what this step achieves
- **Discover** - an open conversation prompt to reason through design decisions
- **What to look for** - what to read and evaluate before moving on
- **Recipe** - a complete implementation prompt you can use as-is or adapt from your own findings

**Where the agent file lands:** the recipes write to `.claude/agents/catalog-test-agent.md`, and because you open Claude Code inside your solution copy of the stack, that path resolves inside the copy rather than in this repository's live agent roster. The same holds for the `.claude/settings.local.json` permission rules the recipes add, which is what makes the "minimal permissions" lesson concrete: the allow and deny lists bind sessions launched in this one project. Your repository roster and your repository settings stay untouched.

**Toolchain you need:** pick a stack you already have installed. Nothing in this lab installs a toolchain for you.

| Stack | Required on PATH | Test framework you will add |
|-------|------------------|-----------------------------|
| `catalog-service-cs` | .NET SDK 10 (`dotnet --version`) | xUnit, via `dotnet new xunit` |
| `catalog-service-java` | JDK 17 or newer and Maven (`mvn -v`) | JUnit 5 and Mockito, already declared |
| `catalog-service-py` | Python 3.10 or newer (`python --version`) | pytest, into a local `.venv` |
| `catalog-service-ts` | Node 18 or newer and npm (`npm -v`) | Vitest, via `npm install --save-dev vitest` |

Step 0 below creates your solution copy with a single `cp -r`. Run that copy from a shell at the repository root first, then launch your session inside the copy. The path in the block below names the C# copy; swap `cs` for `java`, `py` or `ts` to match your stack.

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

Your `-solution` copy is the session folder, not the checked-in starter, so start the session inside the copy. Step 0 below scaffolds it; start the session there once it exists. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd src/food-app/catalog-api/catalog-service-cs-solution
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `catalog-service-cs-solution` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In src/food-app/catalog-api/catalog-service-cs-solution write xUnit tests for FoodController and run dotnet test ....
```

That works for any step whose result is just files. It does not work for the agent or its permission rules: `.claude/agents/` and `.claude/settings.local.json` load from the directory the session was launched in, so a root session writes `catalog-test-agent.md` and the allow and deny lists into the solution folder and then ignores both, leaving Step 3 with no sub-agent and Bash unrestricted. Launch inside `catalog-service-cs-solution` from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.local.json`, because permission rules are read at startup.

Launching inside the project is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and you read them from the repo root, without ever writing into them, and every path in the prompts below is relative to the solution folder.

---

## Step 0: Create Your Solution Folder

**Goal:** Give the agent a working copy so the checked-in starter stays pristine, and give your session a project of its own to launch in.

The four `catalog-service-*` folders are starters. This repo's convention is that a starter carries no build output, no lockfile and no installed packages, and that every run, install and generated file lands in a sibling `-solution/` folder. The agent you are about to build writes test files and installs packages, so point it at a copy. Run the copy from a shell at the repository root, before you open Claude Code:

```bash
cp -r src/food-app/catalog-api/catalog-service-cs src/food-app/catalog-api/catalog-service-cs-solution
```

Swap `cs` for `java`, `py` or `ts` to match your stack. Run the copy once: if the `-solution` folder already exists, `cp -r` nests a second copy inside it instead of overwriting, and the agent then works on the wrong tree. Then add a `.gitignore` inside the new folder so your artifacts never reach `git status`:

```text
bin/
obj/
node_modules/
dist/
.venv/
__pycache__/
target/
*.db
*.db-shm
*.db-wal
```

From here on, `[FOLDER]` means your `-solution` folder, for example `catalog-service-cs-solution`.

> `catalog-service-cs` ships with `food.db`, `food.db-shm`, `food.db-wal` and a stray `package-lock.json` already tracked in git. Those are pre-existing, not something you created. Working in a copy is what keeps your own output distinguishable from them.

---

## Step 1: Survey the Catalog API Stacks

**Goal:** Understand what is available in the catalog-api before choosing a stack for the testing agent.

**Discover:**

```text
Explore .. (the catalog-api folder one level above this project, holding all four stacks). For each subdirectory:
  1. Identify the programming language, primary framework, and build tool.
  2. List the main source files, excluding build output and lock files.
  3. Note whether a test project or test framework configuration already exists.

Format the result as a table with columns: Stack, Language/Framework, Key Source Files, Tests Exist.

Then recommend which stack would be easiest to add unit tests to, and why.
```

**What to look for:** A four-row table covering `catalog-service-cs` (.NET/ASP.NET Core), `catalog-service-java` (Java/Spring Boot with Maven), `catalog-service-py` (Python/Flask), and `catalog-service-ts` (TypeScript/Express). None of the four has test files. Configuration is a different question, and Java is the exception: its `pom.xml` already declares `spring-boot-starter-test`, which brings JUnit 5, Mockito and AssertJ, so the Java path skips the install step entirely. C# already references `coverlet.msbuild` (a coverage tool) but has no test framework. If Claude reports "no tests and no configuration anywhere", it did not open `pom.xml`. Pick the stack you know best for the next two steps. If that is not the stack you copied in Step 0, copy the one you picked instead and reopen your session inside that copy.

---

## Step 2: Design and Build the Testing Agent

**Goal:** Reason through the permission model and test framework for your chosen stack, then create the agent.

**Discover:**

```text
I want to build a unit testing agent for the [STACK] implementation in this project (src/food-app/catalog-api/[FOLDER]). Read the source files here and help me design the agent:

1. What Bash commands does it need? List only what is required to run the test suite and install dependencies. What should it be explicitly denied?
2. The agent should only work inside this one directory. Sub-agent frontmatter has no permissions: block, so where does that constraint actually go?
3. What test framework fits this stack and what naming convention should tests follow?
4. Why should the agent never mock a dependency unless the source code already defines an interface for it? How would you phrase that rule so the agent actually follows it?
```

Replace `[STACK]` and `[FOLDER]` with your choice from Step 0 before pasting.

**What to look for:** Claude should read the actual source files before making recommendations about naming conventions. The answer to question 4 should explain why over-mocking produces tests that pass even when the real integration is broken. Push back on any recommendation that grants broader Bash access than strictly needed. Also apply this test to the deny list: a deny rule for a toolchain the stack cannot reach is decoration. Deny the dangerous subcommands of the tool you just allowed instead, because `Bash(dotnet:*)` also permits `dotnet tool install --global` and `Bash(npm:*)` also permits `npm install -g` and `npm publish`.

### Where permissions actually live

Agent frontmatter has no `permissions:` block. Adding one does not fail loudly: it is ignored, and you ship an agent with unrestricted Bash while believing it is locked to `dotnet`. The per-agent levers are `tools` and `disallowedTools`; the command-level allow and deny rules live in settings and apply to the whole session, sub-agents included. See [demos/06-subagents/01-introduction/readme.md](../../demos/06-subagents/01-introduction/readme.md) for the full field list, and the [sub-agent frontmatter reference](https://code.claude.com/docs/en/sub-agents) for what is supported.

So the recipes below set `permissionMode: dontAsk` in the frontmatter and put the command rules in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": ["Bash(dotnet:*)", "Bash(ls:*)"],
    "deny": ["Bash(git:*)", "Bash(rm:*)", "Bash(dotnet tool:*)"]
  }
}
```

Swap the allow entries for your stack. Settings are read at startup, so restart with `/exit` then `claude` after you write `.claude/settings.local.json`, or the rules do not apply to the session you are in. Be honest with yourself about what this buys you: these rules are session-wide, not per-agent, so they constrain your main conversation too. They are also scoped to this project only, which is exactly why the session is launched here and not at the repo root.

**Recipe (C#/.NET):**

```text
Create .claude/agents/catalog-test-agent.md with this content:

---
name: catalog-test-agent
description: Writes and runs xUnit unit tests for catalog-service-cs at src/food-app/catalog-api/catalog-service-cs-solution. Reads source files, identifies untested public methods, writes test classes, runs dotnet test, and reports pass/fail results.
model: sonnet
permissionMode: dontAsk
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

## Scope

Work only inside this project folder, src/food-app/catalog-api/catalog-service-cs-solution. Do not read or write files outside it.

## Testing Rules

- Use xUnit as the test framework. Create the test project with dotnet new xunit and add a project reference to the service.
- Name test methods using the pattern MethodName_Scenario_ExpectedBehavior.
- Never mock a dependency unless an interface for it already exists in the source code.
- Run the suite with dotnet test from the solution folder.

Then add to .claude/settings.local.json:
  allow: Bash(dotnet:*), Bash(ls:*)
  deny: Bash(git:*), Bash(rm:*), Bash(dotnet tool:*)
```

**Recipe (Java/Spring Boot):**

```text
Create .claude/agents/catalog-test-agent.md with this content:

---
name: catalog-test-agent
description: Writes and runs JUnit 5 unit tests for catalog-service-java at src/food-app/catalog-api/catalog-service-java-solution. Reads source files, identifies untested public methods, writes test classes, runs mvn test, and reports pass/fail results.
model: sonnet
permissionMode: dontAsk
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

## Scope

Work only inside this project folder, src/food-app/catalog-api/catalog-service-java-solution. Do not read or write files outside it.

## Testing Rules

- Use JUnit 5 and Mockito. pom.xml already declares spring-boot-starter-test, so add no new dependencies.
- Place tests under src/test/java mirroring the main package structure.
- Annotate test methods with @DisplayName using plain English descriptions.
- Never mock a dependency unless an interface for it already exists in the source code.
- Run the suite with mvn test from the solution folder.

Then add to .claude/settings.local.json:
  allow: Bash(mvn:*), Bash(ls:*)
  deny: Bash(git:*), Bash(rm:*)
```

**Recipe (Python):**

```text
Create .claude/agents/catalog-test-agent.md with this content:

---
name: catalog-test-agent
description: Writes and runs pytest unit tests for catalog-service-py at src/food-app/catalog-api/catalog-service-py-solution. Reads source files, identifies untested functions and methods, writes test modules, runs pytest, and reports pass/fail results.
model: sonnet
permissionMode: dontAsk
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

## Scope

Work only inside this project folder, src/food-app/catalog-api/catalog-service-py-solution. Do not read or write files outside it.

## Environment

Never install into the system or user Python. Create a virtual environment inside the solution folder first and use it for everything:

  python -m venv .venv
  .venv/Scripts/python -m pip install -r requirements.txt pytest      # Windows
  .venv/bin/python -m pip install -r requirements.txt pytest          # macOS and Linux

Invoke tools through the interpreter (python -m pip, python -m pytest), never through the bare pip or pytest entry points, which only resolve if the Scripts directory is on PATH.

## Testing Rules

- Use pytest as the test framework.
- Name test functions with the prefix test_ followed by the function name and scenario.
- Never mock a dependency unless a protocol or abstract base class for it already exists in the source code.
- Run the suite with .venv/Scripts/python -m pytest (Windows) or .venv/bin/python -m pytest.

Then add to .claude/settings.local.json:
  allow: Bash(python:*), Bash(ls:*)
  deny: Bash(git:*), Bash(rm:*)
```

`Bash(python:*)` alone covers both `python -m pip` and `python -m pytest`, so this stack needs the tightest allow list of the four. That is the "minimal permissions" lesson landing in practice: routing through one entry point shrinks the surface you have to trust. Add `.venv/` to the solution folder's `.gitignore` before the first install.

**Recipe (TypeScript):**

```text
Create .claude/agents/catalog-test-agent.md with this content:

---
name: catalog-test-agent
description: Writes and runs Vitest unit tests for catalog-service-ts at src/food-app/catalog-api/catalog-service-ts-solution. Reads source files, identifies untested exports, writes test files, runs vitest, and reports pass/fail results.
model: sonnet
permissionMode: dontAsk
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

## Scope

Work only inside this project folder, src/food-app/catalog-api/catalog-service-ts-solution. Do not read or write files outside it.

## Testing Rules

- Use Vitest as the test framework; install it with npm install --save-dev vitest if it is not already a dependency.
- Name test files with the suffix .spec.ts and place them alongside the source file they test.
- Never mock a dependency unless an interface or type for it already exists in the source code.
- Run the suite with npx vitest run. The bare npx vitest starts watch mode and never exits.
- package.json has no test script. Add "test": "vitest run" to the scripts block so npm test works too.

Then add to .claude/settings.local.json:
  allow: Bash(npm:*), Bash(npx:*), Bash(ls:*)
  deny: Bash(git:*), Bash(rm:*), Bash(npm:* -g), Bash(npm publish:*)
```

> The recipes above reflect one set of design choices: minimal Bash scope, no git access, interface-only mocking. If your discovery conversation produced different conclusions (different test framework, broader or narrower permissions), write the agent file from your own notes instead.

---

## Step 3: Generate Tests and Evaluate

**Goal:** Run the testing agent against real source code and judge the quality of what it produces, not just whether it runs.

**Discover:**

```text
Use the catalog-test-agent sub-agent on this project (src/food-app/catalog-api/[FOLDER]). The agent should:
  1. Read the source files and identify the class or module with the most public methods.
  2. Write a test file using the configured framework, covering each public method with at least one happy-path test and one edge-case test.
  3. Run the test suite and report pass count, fail count, and any errors.
  4. If a test fails, decide whether the test is wrong or the source is, and report which.

After the agent finishes, read the generated test file yourself and answer: do these tests verify behavior, or do they just confirm the method does not throw? If they feel shallow, what would make them meaningful?
```

Replace `[FOLDER]` with your solution folder from Step 0 before pasting. On the TypeScript path, make sure the agent runs `npx vitest run` and not the bare `npx vitest`, which blocks in watch mode and never reports a count.

**What to look for:** A new test file in your solution folder and a test result summary from the agent. Reading the tests yourself is the key part of this step. Shallow tests (assert not null, assert no exception) are common; if you see them, push the agent to add one more meaningful assertion per test method before calling the step complete.

Expect red on the C# path, and treat that as the point of the exercise. `FoodController.DeleteFood` calls `GetById(id)` without awaiting it, so `item` is a `Task<CatalogItem>` that is never null and always reaches `ctx.Remove(item)`. Any honest behavioral test of that endpoint fails with `System.InvalidOperationException: The entity type 'Task<CatalogItem>' was not found`. A red test that exposes a real bug is the strongest evidence the agent wrote behavioral tests rather than smoke tests.

Fix the source in your solution copy (`var item = await GetById(id);`), not the test, then re-run and watch the suite go green. Note that the endpoint still returns `Ok()` for an unknown id even after the await fix, which is a second bug your edge-case test should catch.
