# Labs - Module 12: Managed Agents

Managed Agents move the agent loop off your machine: Anthropic runs the loop and hosts a container per Session, while you define the Agent once and start Sessions against it. This lab walks the three resources (Agent, Environment, Session) end to end on a real debugging task, then adds the piece that makes autonomy shippable, a human approval gate that parks the Session at `requires_action` until an operator answers. You leave knowing the session state machine, the SSE event model, file mounts, agent versioning, and the difference between the two blocking handoffs.

| Lab | Topic | Title | Track | Level | Time | Description |
|-----|-------|-------|-------|-------|------|-------------|
| 01 | Codebase Triage | [Build a Managed Agent for Codebase Triage](lab-01-managed-agent-codebase-triage.md) | Optional | Advanced | 1h | Mount a broken Python repo into a cloud Session and stream the fix loop until the suite is green. Then publish a second Agent version carrying a `commit_changes` custom tool, and resume the parked Session with both an allow and a deny verdict. |

**Core** is the one lab that teaches this module's central capability; run it if you run nothing else. **Optional** labs go deeper, cover a second tool, or need an account you may not have. **Level** rates the lab itself: Beginner needs no prior Claude Code experience, Intermediate assumes you have configured a harness before, Advanced assumes you are comfortable with hooks, subagents, or headless scripting.

Core path: none, this module is gated. All labs: 1h.

Without beta access this lab is a read-through rather than a build, so treat it as a walkthrough of the Managed Agents surface and skip it if you cannot provision an agent.

The starter is checked in at [`01-triage/calc-triage/`](01-triage/calc-triage/readme.md), carrying the broken Python fixture; you write the two driver scripts, and the completed reference lives beside it in [`01-triage/calc-triage-solution/`](01-triage/calc-triage-solution/readme.md). Everything past Setup calls the live API and bills session-hours plus model tokens, so read the lab's "Before You Start" table before running anything.
