# Select the Right Model

## Available Models

| Model | Best For |
|-------|----------|
| Opus 5 (Default) | Complex reasoning, multi-step planning, challenging architectural decisions, agentic coding |
| Opus 5 (1M context) | Same as Opus but with the extended context window selected explicitly: billed as extra usage |
| Sonnet 5 | Everyday tasks, general-purpose coding, standard workflows, best value |
| Haiku 4.5 | Fastest responses, quick answers, simple lookups, tight token budgets (200K context) |

Opus 4.8, Opus 4.7, and Sonnet 4.6 remain selectable for teams that pinned an older model, but new work should start on the Claude 5 family.

## Fast Mode

Fast mode runs Claude Opus with faster output rather than downgrading to a smaller model. Toggle it with `/fast`. It is available on Opus 5, Opus 4.8, and Opus 4.7, and it is priced above standard Opus usage, so reach for it when turnaround matters more than token spend.

## Token Usage & Cost Awareness

Defaulting to the strongest model (Opus) on every task wastes tokens and increases costs unnecessarily. Haiku handles most everyday coding tasks efficiently and costs a fraction of Opus, while Sonnet provides an excellent middle ground for moderately complex work. Save Opus for situations where the task genuinely requires its advanced reasoning capabilities, such as complex system design or intricate debugging. By matching model strength to task complexity, you optimize both spending and response latency without sacrificing quality.

## Working Past Your Plan Limit

Subscription plans meter usage against a per-seat allowance rather than a token balance. When you hit it, usage credits let you keep working, and `/usage-credits` opens the right place for your role: billing settings for a Pro or Max subscriber, the organization's usage settings for a Team or Enterprise member with billing access, and a request to your admins for everyone else. The command needs a claude.ai login through `/login` and is unavailable with API key authentication.

Run `/usage` to see where you stand. On a paid plan it also breaks recent usage down by skill, subagent, plugin, and MCP server, and flags any behaviour accounting for 10% or more of it.

## The Other Half of the Bill

Tier selection is one lever, and it is the smaller one in a long session. What you send every turn matters more than which model reads it, because the whole conversation ships with every message. [05: Prompt Caching](../05-prompt-caching/readme.md) covers the mechanism that makes that affordable and the actions that throw it away, including the `/model` switch this topic is about.

## Helpful Claude Slash Commands

| Command | Usage |
|---------|-------|
| `/model` | Switch the active model mid-session without restarting |
| `/fast` | Toggle fast mode on an Opus model for higher output speed |
| `/usage` | Show token usage and estimated cost for the current session; `/cost` is an alias |
| `/compact` | Compress conversation history to reduce context size and cost |
| `/status` | Display current model, context usage, and session info |

## Key Topics covered in this module

- [Anthropic model overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Claude Code model configuration](https://code.claude.com/docs/en/settings)
- [Claude pricing](https://www.anthropic.com/pricing)
