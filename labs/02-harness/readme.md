# Labs - Module 02: Harness

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Harness Elements | [Install a React Agent Skill](lab-01-react-skill.md) | Optional | Beginner | 30m | Install the ready-made vercel-react-best-practices skill from skills.sh into the React app's own .claude/skills/vercel-react-best-practices and confirm it is active before the harness lab uses it. |
| 02 | Harness Configuration | [Configure the Harness on a Broken React App](lab-02-fix-the-react-food-shop.md) | Core | Intermediate | 1h 15m | Configure the Claude Code harness piece by piece, then watch everything work together as Claude fixes a broken React app. |
| 03 | Prompting | [Apply Prompting Techniques](lab-03-prompting-techniques.md) | Optional | Intermediate | 50m | Apply five prompting techniques to your harness: statefile maintenance, anchors, @-mentions, few-shot examples in `CLAUDE.md`, and slash-command promotion. |
| 04 | Mods | [Build an Ask-Check Mod Test-First](lab-04-ask-check.md) | Optional | Advanced | 1h 20m | Build a mod that spots a question you already answered, shows your earlier sentence in a band above the prompt and sends it back on one key, growing it step by step until its six tests pass. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: 1h 15m. All labs: 3h 55m.

Each lab has its own starter folder here, with the finished counterpart beside it:

| Lab | Starter | Solution |
|-----|---------|----------|
| 01 | `lab-01-react-skill/` | `lab-01-react-skill-solution/` |
| 02 | `lab-02-food-shop/` | `lab-02-food-shop-solution/` |
| 03 | `lab-03-users-api/` | `lab-03-users-api-solution/` |
| 04 | `lab-04-ask-check/` | `lab-04-ask-check-solution/` |

Lab 02's starter holds all three pieces the lab needs: the React app at `shop-ui/food-shop-react`, the catalog API at `catalog-api/catalog-service-cs`, and the Angular app at `shop-ui/food-shop-ng` that Task 6 reads the checkout form from. Starters stay pristine (no dependencies, no build output); install, run and generate only inside the solution folders, and use them as the completed reference when you want to compare.

Lab 02 Tasks 5 and 6 invoke the React skill that Lab 01 installs. The two labs are separate projects, so Lab 02 tells you how to copy the skill across before Task 5; skip Lab 01 and those two tasks still work, they just run without the skill's conventions.

## Where to Open Claude Code

All four labs build their own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starters are already in this repo, so there is nothing to scaffold: change into the one your lab uses and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/02-harness/lab-01-react-skill
claude
```

```bash
cd labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react
claude
```

```bash
cd labs/02-harness/lab-03-users-api
claude
```

```bash
cd labs/02-harness/lab-04-ask-check
claude --plugin-dir .
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open the starter as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the commands above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/02-harness/lab-02-food-shop/shop-ui/food-shop-react fix the Checkout button so it enables when the cart has at least one item ....
```

That works for any step whose result is just files. It does not work for the harness steps: hooks in `.claude/settings.json`, `.claude/commands/`, `.claude/skills/` and `.mcp.json` load from the directory the session was launched in, so a root session writes them into the lab folder and then ignores them. Launch inside the starter from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to these labs, with each starter as the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. All four labs read from them and none writes into them.
