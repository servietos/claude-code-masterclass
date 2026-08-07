# Optimize the Agentic Harness

Claude Code sessions have a hidden cost structure that most teams discover too late. Every file loaded through CLAUDE.md is included on every turn, every developer on the team pays the same token overhead, and every session compounds those costs across a sprint. This module treats the agentic harness as software: something that can be profiled, measured, and improved systematically using the same discipline engineers apply to application code.

## Why Optimization Matters

A 1,700-token CLAUDE.md running twenty turns per session, twenty sessions per sprint, and five developers consumes 3.4 million tokens on context alone before a single line of feature code is generated. The multiplication effect is the key insight: a 30% reduction in CLAUDE.md size saves more tokens in a week than most conversation-level optimizations save in a month.

The same logic applies to prompt quality. A skill that produces inconsistent output forces re-runs, manual verification, and cleanup. That rework accumulates across every developer and every sprint, often costing far more than the initial investment in a rigorous improvement cycle. Measuring consistency is not optional for any skill used in production workflows.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/context` | Show what currently occupies the context window and which files dominate it. |
| `/usage` | Read session cost and token usage before and after an optimization (`/cost` is an alias). |
| `/compact` | Compact the conversation on demand instead of waiting for auto-compaction. |
| `/memory` | Open the CLAUDE.md files that load on every turn, to compress them. |

## Key Topics Covered in This Module

- [Manage costs effectively](https://code.claude.com/docs/en/costs): token usage tracking, `/usage`, and the levers that reduce spend
- [Manage Claude's memory](https://code.claude.com/docs/en/memory): how CLAUDE.md files and imports load into every turn
- [Skills](https://code.claude.com/docs/en/skills): why skill bodies load on demand while CLAUDE.md content is a recurring cost
