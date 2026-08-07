# Drive Specs with Spec Kit and BMAD

Hand-driven Plan Mode is always available, but two open-source frameworks formalise the same workflow into installable tooling. Understanding all three lets you reach for the right tool based on the size of the work, the familiarity of the domain, and who needs to read the artefacts.

## The Three Planning Traditions

| Approach | What it generates | Pipeline |
|---|---|---|
| Plan Mode by hand | STATE.md, work packages | You drive every step |
| Spec Kit | constitution, spec.md, plan.md, tasks.md | Four slash commands in order |
| BMAD-METHOD | PRD, architecture.md, story files | PM, Architect, Developer agent chain |

All three produce the same logical artefacts: governing principles, feature spec, technical plan, task list. They differ in how much they formalise and for whom the output is written.

## Spec Kit

Spec Kit ships a CLI (`specify`) and a set of Claude Code slash commands prefixed `/speckit.*`. It enforces a four-step pipeline: constitution, specify, plan, tasks, implement. Output is agent-readable, terse, and structured for automated consumption.

The constitution step is the highest-value part. It forces you to write down governing principles before any feature work begins, making them available to every subsequent step in the pipeline. On familiar domains you skip this discipline; Spec Kit makes it mandatory.

Best for: unfamiliar domains where the constitution's constraint discipline has the most value, or teams that need enforced consistency across all feature work. The overhead is non-trivial for a one-hour feature; on a two-day migration it pays for itself.

## BMAD-METHOD

BMAD-METHOD (Breakthrough Method for Agile AI-Driven Development) is an open-source framework that structures AI-assisted development as a conversation between specialized agents, each playing a distinct role in the software delivery process. Instead of one general-purpose Claude session doing everything, BMAD assigns dedicated personas: a Product Manager who writes requirements, an Architect who makes technical decisions, a Developer who breaks work into implementable stories, and a QA agent who validates outcomes. Each agent is a Claude instance loaded with a specific system prompt and a defined set of responsibilities.

The key idea is that different stages of a feature need different thinking modes. A PM agent asks "what problem are we solving and for whom?" before anyone touches a schema. An Architect agent asks "what are the trade-offs between these three approaches?" before anyone writes a migration. Separating those concerns into separate agent invocations prevents the common failure where Claude conflates product intent with implementation detail in a single response.

BMAD supports two invocation modes. Sequential mode: you invoke each agent in order (PM, then Architect, then Developer), reviewing and approving each agent's output before the next one starts. Party mode: all agents collaborate in a single session, surfacing disagreements between roles in real time. Sequential is better for complex work where you want a human checkpoint between stages; party mode is faster for smaller features where the trade-off review can happen in one sitting.

Output is human-readable by design. BMAD's PRD is written for a product manager or stakeholder audience, not for an agent to consume programmatically. The architecture document is written for engineers who need to understand the rationale, not just the decision. Story files are written for a developer (human or AI) to pick up and execute one at a time.

This is the main difference from Spec Kit: Spec Kit produces agent-readable artefacts optimized for automation; BMAD produces stakeholder-readable artefacts optimized for review and sign-off.

Best for: features where non-engineering stakeholders need to read and approve the artefacts before implementation begins. The overhead is the highest of the three; BMAD produces the most pages. On a one-hour feature it is ceremony; on a multi-week initiative the PRD and architecture doc earn their length by preventing misalignment before code is written.

## When to Reach for Each

| Approach | Reach for it when |
|---|---|
| Plan Mode by hand | You know the domain well and want speed; overhead of a framework is not justified |
| Spec Kit | Domain is unfamiliar, or the team needs enforced pipeline discipline across all feature work |
| BMAD-METHOD | Artefacts need to be readable by PMs or designers, not just agents |

## Demos

| Topic | Description |
|---|---|
| [Spec Kit](demo-spec-kit-pipeline.md) | Push a tag-search feature through constitution, specify, plan, tasks and implement, then compare the generated spec against a hand-written STATE.md. |
| [BMAD-METHOD](demo-bmad-agent-chain.md) | Run the same feature through the PM, Architect and Developer chain, try party mode, and put the PRD next to Spec Kit's spec. |

## Starter and Solution Folders

Work in [notes-cli/](notes-cli/) via each demo's setup script, which copies it outside this repository because both frameworks initialise their own git repo; the finished feature is in [notes-cli-solution/](notes-cli-solution/).

## Key Topics Covered in This Module

- [Spec Kit on GitHub](https://github.com/github/spec-kit): source, README, and slash command definitions
- [BMAD-METHOD on GitHub](https://github.com/bmad-code-org/BMAD-METHOD): agent roster, install instructions, and party-mode documentation
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking): used inside all three traditions for hard architectural decisions
- [Claude Code memory (CLAUDE.md)](https://code.claude.com/docs/en/memory): encoding STATE.md rules and constitution principles that persist across sessions
