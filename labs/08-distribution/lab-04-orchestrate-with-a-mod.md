# Route and Brief Subagents With a Mod

Build `desk-router`, a mod that sends lookups to a cheap read-only agent, attaches the same brief to every subagent and keeps a ledger you print with `/desk`. You develop it in a marketplace folder of its own, prove it with `claude plugin test`, then install it from that marketplace into the class repo.

What you practice here: turning delegation rules into hooks that run on every prompt and every subagent spawn.

Duration: about 65 minutes.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **Why this matters:** Your delegation rules live in a `CLAUDE.md` paragraph today: send lookups to a cheap agent, tell every subagent not to edit, keep reports short. The model reads that paragraph and follows it when it remembers. A mod turns the rules into code: the hint reaches the model with every lookup, and the brief and the reroute run on every spawn whatever the model chose.

> **Why a marketplace folder of its own:** one mod serves many repositories. Developing it in its own marketplace folder keeps its code apart from every project it steers, and each project installs it by name. The class repo is the first such project here.

> **Two folders:** [`04-orchestrate/delegation-desk/`](04-orchestrate/delegation-desk/) holds `shop-api/`, a small Python shop to ask questions about. Beside it, [`04-orchestrate/desk-marketplace/`](04-orchestrate/desk-marketplace/) is the marketplace folder you develop the mod in, with `plugins/desk-router/` holding nothing but its `plugin.json`. You write the agent, the hooks module, the state contract, the tests and the catalog there. The completed marketplace is checked in as [`04-orchestrate/desk-marketplace-solution/`](04-orchestrate/desk-marketplace-solution/); build your own first and use it to compare.

---

## Where to Open Claude Code

Open the session inside the shop and load the plugin from the marketplace folder. Run this from the repo root; both commands work unchanged in PowerShell:

```bash
cd labs/08-distribution/04-orchestrate/delegation-desk
claude --plugin-dir ../desk-marketplace/plugins/desk-router
```

`--plugin-dir` loads the plugin from disk for this session only, nothing is installed. The session reads the plugin's agents and its hooks module when it starts, so every step that changes the mod ends with a restart: `/exit`, then the same `claude --plugin-dir ../desk-marketplace/plugins/desk-router`.

Keep a second terminal in `labs/08-distribution/04-orchestrate/desk-marketplace/` for the shell commands. That folder is where you develop the mod: every file path in Steps 2 to 6 is relative to it.

This lab was run on Claude Code 2.1.312. Hooks modules are an early-access API that moves between releases; `claude --version` shows yours.

> **Note:** if you already run mods of your own that steer subagents, add `--setting-sources project,local` to the `claude` command. It leaves your user settings out of the session, and with them every plugin you installed, so only `desk-router` hooks the spawns.

---

## Setup: Look at the Starter

```text
04-orchestrate/
├── delegation-desk/
│   └── shop-api/
│       ├── app.py                           places one order and prints it
│       ├── inventory.py                     stock, reservations, low-stock list
│       ├── orders.py                        order lines and totals
│       ├── pricing.py                       loyalty discount, shipping, tax
│       └── settings.py                      every rate and threshold
└── desk-marketplace/
    └── plugins/
        └── desk-router/
            └── .claude-plugin/plugin.json   name desk-router, version 0.1.0
```

Validate the empty plugin from the second terminal:

```bash
claude plugin validate plugins/desk-router
```

**Expected result:** `✔ Validation passed`. The report validates the manifest and nothing else: no hooks, no agents. The plugin-directory block warns about a missing icon, which does not change the verdict.

---

## Step 1: Ask a Lookup Without the Mod

**Goal:** See where a lookup runs today, so you can recognise the change in Step 3.

A lookup answered on the main thread puts every file it opened into the context of your session, and you pay for that context on every later turn.

**Prompt (in the Claude Code session):**

```text
Where is the loyalty discount calculated in shop-api, and what caps it?
```

**Expected result:** an answer naming `loyalty_discount` in `shop-api/pricing.py` and `MAX_LOYALTY_DISCOUNT = 0.15` in `shop-api/settings.py`. The transcript shows the main session's own `Grep` or `Read` calls and no `Agent` call. Which tools Claude picks varies from run to run; what matters is that no subagent appears.

---

## Step 2: Add a Read-Only Scout Agent

**Goal:** Give the plugin an agent that can only read and runs on the cheapest model, as the target for every lookup.

A plugin's agent is typed `<plugin>:<name>`, so this file becomes `desk-router:scout`. `tools` limits it to the three read tools, and `model: haiku` runs it on Haiku whatever model your session uses.

Create `plugins/desk-router/agents/scout.md` in your editor:

```markdown
---
name: scout
description: Read-only lookup agent. Use for questions that only need facts from the code, such as where something is defined, which files use it, or what a function does. It reads and searches, never edits.
tools: Read, Glob, Grep
model: haiku
---

You answer one lookup about the code in the current folder. Search with Glob and Grep, read only the lines you need, and quote what you found. Say what you could not find. Never guess.
```

Restart the session (`/exit`, then `claude --plugin-dir ../desk-marketplace/plugins/desk-router`) and ask:

**Prompt (in the Claude Code session):**

```text
Which agent types whose name starts with desk-router can you delegate to? Answer with the names only.
```

**Expected result:** `desk-router:scout`. The agent is in the roster, and nothing sends work to it yet: a roster entry only names a target.

---

## Step 3: Hint the Model to Delegate Lookups

**Goal:** Write the hooks module with its first hook: on every lookup the user types, attach a hint that names the scout.

A mod is a plugin whose `hooks/hooks.json` names one hooks module. The module exports `register(on)`, and every hook has the shape `($, e, next)`: `e` is the event's input, `next(e)` runs the rest of the chain, and `next({ ...e, context })` attaches a block the model reads and the user never sees. `e.origin.kind` keeps out prompts that a task notification or another plugin submitted, and `e.command` is set for slash commands.

Create `plugins/desk-router/hooks/hooks.json`:

```json
{ "modules": ["./router.ts"] }
```

Create `plugins/desk-router/hooks/router.ts`:

```typescript
import type { Register } from 'claude-code'

const SCOUT = 'desk-router:scout'
const PEOPLE = new Set(['composer', 'bridge', 'sdk'])
const LOOKUP = /\b(where (is|are|does|do)|which (files?|modules?|functions?)|what (does|do|reads|calls)|find|locate|list)\b/i
const HINT = `desk-router: this prompt is a lookup. Delegate it to the ${SCOUT} agent and answer from its report.`

export const register: Register = on => {
  on('prompt.submit', ($, e, next) =>
    PEOPLE.has(e.origin.kind) && !e.command && LOOKUP.test(e.text)
      ? next({ ...e, context: [...(e.context ?? []), HINT] })
      : next(e),
  )
}
```

**Command:**

```bash
claude plugin validate plugins/desk-router
```

**Expected result:** the hooks section of the report lists what the module hooks and calls, then the verdict:

```text
  ❯ ./router.ts hooks: prompt.submit
  ❯ ./router.ts gating hook without .catch: prompt.submit
  ❯ ./router.ts calls: nothing on $
```

The gating line states a fact: a hook that fails here is skipped and the prompt goes through untouched. Restart the session, then ask a new lookup:

**Prompt (in the Claude Code session):**

```text
Where is the shipping fee defined in shop-api, and when is it waived?
```

**Expected result:** the transcript shows an `Agent` call to `desk-router:scout`. The scout runs in the background, so Claude may first say that the scout is still searching and answer once its report arrives: `SHIPPING_FEE = 4.90` in `shop-api/settings.py`, waived from `FREE_SHIPPING_FROM = 50.00` by `shipping()` in `shop-api/pricing.py`. The hint is advice the model reads, so a model can still ignore it; the next step adds the part that is enforced.

---

## Step 4: Brief and Reroute Every Spawn, and Keep a Ledger

**Goal:** Make the delegation rules code: every subagent gets the same brief, a generic agent asked for a lookup is swapped for the scout, and every spawn lands in a ledger that `/desk` prints.

`agent.spawn` fires before any subagent starts. `next({ ...e, subagentType, prompt })` starts a different agent with a longer prompt, and `next` resolves to the model it started on. A resumed agent can only be refused, a workflow agent keeps its type and a fork dispatches no other, so the hook passes those through. The ledger is an `atom` in `$.state`: it lives as long as the session, survives a reload of the module, and its type is declared in a contract file that `plugin.json` names.

Create `plugins/desk-router/types/index.d.ts`:

```typescript
export type Delegation = {
  subagentType: string
  description: string
  model: string
  isRerouted: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'desk-router': { ledger: Delegation[] }
  }
}
```

Name the contract in `plugins/desk-router/.claude-plugin/plugin.json`: put a comma after `"license": "MIT"` and add this line below it:

```json
  "types": "./types/index.d.ts"
```

Replace `plugins/desk-router/hooks/router.ts` with:

```typescript
import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Delegation } from '../types'

const SCOUT = 'desk-router:scout'
const GENERIC = new Set(['general-purpose', 'Explore'])
const PEOPLE = new Set(['composer', 'bridge', 'sdk'])
const LOOKUP = /\b(where (is|are|does|do)|which (files?|modules?|functions?)|what (does|do|reads|calls)|find|locate|list)\b/i
const HINT = `desk-router: this prompt is a lookup. Delegate it to the ${SCOUT} agent and answer from its report.`
const BRIEF = [
  '[desk-router brief]',
  '- Read only: never edit or write a file.',
  '- Cite every fact as path:line.',
  '- Report in at most 1500 characters.',
].join('\n')

const ledger = atom({ plugin: 'desk-router', key: 'ledger' } as const, [])

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'desk', description: 'List the subagents desk-router briefed in this session' })

    return next(e)
  })

  on('prompt.submit', ($, e, next) =>
    PEOPLE.has(e.origin.kind) && !e.command && LOOKUP.test(e.text)
      ? next({ ...e, context: [...(e.context ?? []), HINT] })
      : next(e),
  )

  on('agent.spawn', async ($, e, next) => {
    if (e.resume || e.workflow || e.fork) {
      return next(e)
    }

    const isRerouted = GENERIC.has(e.subagentType) && LOOKUP.test(`${e.description} ${e.prompt}`)
    const subagentType = isRerouted ? SCOUT : e.subagentType
    const started = await next({ ...e, subagentType, prompt: `${e.prompt}\n\n${BRIEF}` })
    const entry: Delegation = { subagentType, description: e.description, model: started.model ?? 'denied', isRerouted }
    await update($, ledger, all => [...all, entry])

    return started
  })

  on('command.run', { command: 'desk' }, async $ => {
    const list = await read($, ledger)
    const rows = list.map((one, i) => `${i + 1}. ${one.subagentType} on ${one.model}${one.isRerouted ? ' (rerouted)' : ''}: ${one.description}`)

    return { text: rows.length > 0 ? rows.join('\n') : 'No subagent briefed yet.' }
  })
}
```

**Command:**

```bash
claude plugin validate plugins/desk-router
```

**Expected result:** the report now names the contract and four hooks:

```text
  ❯ types ./types/index.d.ts declares state: desk-router.ledger
  ❯ ./router.ts hooks: session.start, prompt.submit, agent.spawn, command.run{command=desk}
  ❯ ./router.ts answers its own command: command.run{command=desk}
  ❯ ./router.ts calls: $.command.register, $.state.get, $.state.set
  ❯ ./router.ts state writes: desk-router.ledger
```

Restart the session and ask for the wrong agent on purpose:

**Prompt (in the Claude Code session):**

```text
Use a general-purpose subagent to find which modules in shop-api read TAX_RATE.
```

When the answer is in, print the ledger:

```text
/desk
```

**Expected result:** the transcript's `Agent` call says `general-purpose`, and Claude's answer may even say it used one. The ledger tells you what actually ran:

```text
desk-router: 1. desk-router:scout on claude-haiku-5-5 (rerouted): Find TAX_RATE readers in shop-api
```

The description is the one Claude wrote and varies, and the model id follows your Claude Code version. The answer names `pricing.py` as the one module that imports and uses `TAX_RATE`. The scout ran on Haiku with the brief appended to its prompt, which the next step proves.

---

## Step 5: Prove the Routing With Tests

**Goal:** Pin the routing down with tests that run in under a second and cost nothing, so a later edit cannot break it unnoticed.

`claude plugin test` runs every `*.test.ts` under the folder against the engine itself. A test gets the engine's `$` and an `on` whose hooks sit beneath the plugin: they stand for the engine, so a test's `agent.spawn` hook receives exactly what the engine would start, the brief included.

Create `plugins/desk-router/tests/router.test.ts`:

```typescript
import { expect, test } from 'claude-code/testing'

const PROMPT = { origin: { kind: 'composer' }, wait: false } as const

const SPAWN = {
  tool_use_id: 'toolu_1',
  description: 'Find the loyalty discount',
  prompt: 'Where is the loyalty discount calculated in shop-api?',
  subagentType: 'general-purpose',
  provider: { plugin: 'engine', tier: 'core' },
  parentModel: 'claude-sonnet-5-5',
  background: false,
  fork: false,
} as const

test('a lookup prompt carries the delegation hint', async ($, on) => {
  let context: readonly string[] = []
  on('prompt.submit', (_, e) => {
    context = e.context ?? []

    return { text: e.text }
  })

  await $.prompt.submit({ ...PROMPT, text: 'Where is the loyalty discount calculated?' })

  expect(context.join('\n')).toContain('desk-router:scout')
})

test('a prompt that changes code carries no hint', async ($, on) => {
  let context: readonly string[] = []
  on('prompt.submit', (_, e) => {
    context = e.context ?? []

    return { text: e.text }
  })

  await $.prompt.submit({ ...PROMPT, text: 'Raise the shipping fee to 5.90' })

  expect(context).toEqual([])
})

test('a generic lookup spawn goes to the scout with the brief', async ($, on) => {
  let spawned = { subagentType: '', prompt: '' }
  on('agent.spawn', (_, e) => {
    spawned = { subagentType: e.subagentType, prompt: e.prompt }

    return { model: 'claude-haiku-5-5', agentId: 'a1' }
  })

  await $.agent.spawn(SPAWN)

  expect(spawned.subagentType).toBe('desk-router:scout')
  expect(spawned.prompt).toContain('[desk-router brief]')
})

test('a named specialist keeps its type and still gets the brief', async ($, on) => {
  let spawned = { subagentType: '', prompt: '' }
  on('agent.spawn', (_, e) => {
    spawned = { subagentType: e.subagentType, prompt: e.prompt }

    return { model: 'claude-sonnet-5-5', agentId: 'a2' }
  })

  await $.agent.spawn({ ...SPAWN, subagentType: 'Plan', description: 'Plan the shipping change' })

  expect(spawned.subagentType).toBe('Plan')
  expect(spawned.prompt).toContain('[desk-router brief]')
})

test('/desk lists every briefed subagent', async ($, on) => {
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('command.register', () => ({ value: { command: 'desk' } }))
  on('agent.spawn', () => ({ model: 'claude-haiku-5-5', agentId: 'a3' }))

  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN)
  const answer = await $.command.run({
    command: 'desk',
    args: '',
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 80 },
  })

  expect(answer.text).toContain('desk-router:scout on claude-haiku-5-5 (rerouted)')
})
```

**Command:**

```bash
claude plugin test plugins/desk-router
```

**Expected result:**

```text
 5 pass
 0 fail
Ran 5 tests across 1 file.
```

Now break the routing on purpose. In `plugins/desk-router/hooks/router.ts` change the `GENERIC` line to `new Set(['Explore'])`, save, and run `claude plugin test plugins/desk-router` again.

**Expected result:** `3 pass` and `2 fail`. The two failures are `a generic lookup spawn goes to the scout with the brief` and `/desk lists every briefed subagent`: a `general-purpose` lookup is no longer rerouted. Put `'general-purpose', ` back in front of `'Explore'` and run the tests once more to see `5 pass`.

---

## Step 6: Turn the Folder Into a Marketplace

**Goal:** List `desk-router` in a catalog at the root of `desk-marketplace/`, so any repository installs the mod by name.

A mod ships exactly like the plugins of Lab 03: a `marketplace.json` lists it, and a relative `source` points at its folder. The catalog is `desk-marketplace/` itself, the folder you developed the mod in. A second mod later gets its own folder under `plugins/` and its own entry in the list.

Create `.claude-plugin/marketplace.json` in `desk-marketplace/`, beside `plugins/`:

```json
{
  "name": "desk-marketplace",
  "owner": { "name": "Claude Code Masterclass" },
  "metadata": { "description": "Lab catalog that ships the desk-router mod." },
  "plugins": [
    {
      "name": "desk-router",
      "version": "0.1.0",
      "description": "Routes lookups to a read-only scout agent, briefs every subagent and keeps a ledger of the delegations.",
      "source": "./plugins/desk-router"
    }
  ]
}
```

**Command:**

```bash
claude plugin validate .
```

**Expected result:** `Validating marketplace manifest` followed by `✔ Validation passed`.

---

## Step 7: Install the Mod Into the Class Repo

**Goal:** Install from the marketplace into the class repo at project scope, the scope a team commits, and see the mod load with no `--plugin-dir`.

`--scope project` writes the catalog and the install into the `.claude/settings.json` of the folder you run it in. Run it from the root of the class repo, so both land in the repo's own `.claude/settings.json` beside the `hooks` and `env` it already holds. A project install is read where a session starts: a session started in a subfolder such as `delegation-desk/` lists the mod as disabled.

Exit the session first (`/exit`). In the second terminal, go up to the repo root and install:

```bash
cd ../../../..
claude plugin marketplace add ./labs/08-distribution/04-orchestrate/desk-marketplace --scope project
claude plugin install desk-router@desk-marketplace --scope project
claude plugin list
```

The path needs the `./`: without it the CLI reads `labs/...` as a GitHub `owner/repo` shorthand and refuses it.

**Expected result:** `✔ Successfully added marketplace: desk-marketplace (declared in project settings)`, `✔ Successfully installed plugin: desk-router@desk-marketplace (scope: project)`, and a list entry for the mod, read straight from your marketplace folder:

```text
  ❯ desk-router@desk-marketplace
    Version: 0.1.0
    Read from: <full path of your desk-marketplace/plugins/desk-router folder>
    Scope: project
    Status: ✔ enabled
```

The repo's `.claude/settings.json` now carries two more keys: the catalog under `extraKnownMarketplaces` as a `directory` source with the absolute path of your `desk-marketplace/` folder, and the mod under `enabledPlugins` as `"desk-router@desk-marketplace": true`. An absolute path only resolves on your machine, so the catalog a team commits names a repository (`owner/repo`), as in Lab 03. Start a plain session at the repo root, with no plugin flag (add `--setting-sources project,local` if you used it so far; the project install still loads):

```bash
claude
```

**Prompt (in the Claude Code session):**

```text
Which module in labs/08-distribution/04-orchestrate/delegation-desk/shop-api lists the products that run low on stock?
```

Then:

```text
/desk
```

**Expected result:** an `Agent` call to `desk-router:scout`, the answer `low_stock()` in `delegation-desk/shop-api/inventory.py`, and a `/desk` row naming `desk-router:scout` on Haiku. The mod now loads from the install in the class repo.

The install reads the plugin straight from your marketplace folder, so you keep developing there: an edit in `desk-marketplace/plugins/desk-router/` reaches the class repo on the next session start, with no reinstall.

---

## Step 8: Clean Up and Compare

**Goal:** Remove the install and the catalog from the class repo, and compare your marketplace with the reference.

Exit the session (`/exit`), then in the second terminal at the repo root:

```bash
claude plugin uninstall desk-router@desk-marketplace --scope project
claude plugin marketplace remove desk-marketplace --scope project
claude plugin list
```

**Expected result:** `✔ Successfully uninstalled plugin: desk-router (scope: project)` and `✔ Successfully removed marketplace: desk-marketplace (from project settings)`. `claude plugin list` no longer shows `desk-router@desk-marketplace`; other plugins on your machine stay in the list.

The repo's `.claude/settings.json` is left with an empty `enabledPlugins` and an empty `extraKnownMarketplaces`, and the CLI rewrote the file with `env` above `hooks`. `git restore .claude/settings.json` returns it to its checked-in state.

Compare your `desk-marketplace/` with [`04-orchestrate/desk-marketplace-solution/`](04-orchestrate/desk-marketplace-solution/). Two extras in yours come from the engine, which writes them for your editor while a session loads the plugin: `plugins/desk-router/.claude-plugin/types/` holds the API declarations and ignores itself with a `.gitignore` of `*`, and `plugins/desk-router/tsconfig.json` extends `./.claude-plugin/types/tsconfig.json`.

---

## What You Just Practised

| Mechanic | Step | Why it matters |
|---|---|---|
| A plugin agent with `tools` and `model` | 2 | A read-only target on the cheapest model, typed `desk-router:scout` |
| `prompt.submit` and `next({ ...e, context })` | 3 | A hint the model reads on every lookup, invisible to the user |
| `claude plugin validate` on a hooks module | 3, 4 | Shows what the module hooks, calls and stores before a session loads it |
| `agent.spawn` rewriting `subagentType` and `prompt` | 4 | The reroute and the brief hold whatever agent the model asked for |
| `$.state` atom with a contract, `/desk` via `command.run` | 4 | A ledger of what really ran, which the model's own account can contradict |
| `claude plugin test` with engine-standing hooks | 5 | Routing pinned by tests that see exactly what the engine would start |
| A marketplace folder of its own with `marketplace.json` | 6 | The mod lives apart from every project it steers and installs by name |
| A project-scope install into the class repo | 7 | A mod ships to a team like any plugin, and an edit in the marketplace reaches it on restart |

[Lab 01](lab-01-build-a-plugin.md) packaged a harness into a plugin and [Lab 03](lab-03-publish-to-a-team-catalog.md) published one through a catalog. This lab puts code inside the plugin that steers how Claude delegates, develops it in its own marketplace and installs it into the class repo.
