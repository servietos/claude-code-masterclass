# Skill from a Proven Conversation (Starter)

The starter for [demo-skill-from-conversation.md](../demo-skill-from-conversation.md). It ships only `.claude/settings.json`, which sets `data-aggregator` to `user-invocable-only`: the finished reference stays out of automatic triggering, so the Step 2 trigger test can only fire your skill, and `/data-aggregator` still works when you type it. This demo is generative, so every other artifact in it is something you prompt Claude to write.

## What you will create here

| File | Step | What it is |
|---|---|---|
| `sales-by-region.js` | 1 | The dependency-free aggregation module the Step 1 recipe asks for |
| `.claude/skills/my-data-aggregator/SKILL.md` | 2 | The skill that encodes that decision sequence, written into this repository's harness |

The skill is named `my-data-aggregator` rather than `data-aggregator` because the finished reference already ships as `data-aggregator` in this repository's `.claude/skills/`. The prefix keeps both, so you can compare your version against the reference with `/data-aggregator` still working.

## Setup

```bash
cd demos/03-skills/02-creating/skill-from-conversation
claude
```

Everything you create is untracked, so the guide's Cleanup section removes it with git. The completed reference lives beside this folder as [skill-from-conversation-solution](../skill-from-conversation-solution/readme.md).
