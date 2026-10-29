# Coordinate Agents with Multiagent, Outcomes and Memory

A single agent reads every input itself, decides alone when it is finished, and starts every session with an empty head. Managed Agents answers each of those limits with one feature: the multiagent block hands work to other agents in isolated threads, an outcome lets a separate grader decide when the work meets a rubric, and a memory store carries what the agent learned into the next session. The scripts in this topic need `anthropic` 1.15.0 or later, because memory stores and the `multiagent_20261001` types arrived after the version the earlier topics pin.

## Three Limits of a Single Agent

| Limit | What goes wrong | Feature that removes it |
|---|---|---|
| Every file lands in one context | Reading crowds out reasoning, and each page is billed at the lead model's rate | Multiagent: subagents, each in its own thread |
| Done is whatever the agent says | A first draft ships with a missing section or a wrong format | Outcomes: a rubric and a grader with its own context |
| Every session starts empty | House style is re-explained in every prompt and lessons are lost | Memory stores mounted into the container |

The three combine in one session, and the demo below uses all of them in a single run. Each also works alone, so adopt the one that matches the pain you have today.

## The Multiagent Block on the Agent

Delegation is configured on the agent that the session runs, in a top-level `multiagent` field beside `system` and `tools`. Nothing changes on `sessions.create()`: the session resolves the setup from the agent's stored configuration. The `multiagent_20261001` type has three members, and each one is switched on or off on its own.

| Member | What it turns on | Agents you list | Default |
|---|---|---|---|
| `subagents` | The agent delegates tasks and reads what each subagent reports | `subagents.predefined_agents`, up to 20 | Enabled |
| `workflows` | Dynamic workflows: the agent writes a program that runs many agents in the background | `workflows.predefined_agents`, up to 20 | Enabled |
| `advisor` | An advisor model the primary thread consults mid-turn | None; set `model` | Disabled |

This is the block the demo's lead agent carries: one listed reader, no agents the lead invents itself, and no workflow runs.

```python
multiagent={
    "type": "multiagent_20261001",
    "subagents": {
        "type": "enabled",
        "predefined_agents": [reader.id],
        "inline_agents": {"type": "disabled"},
    },
    "workflows": {"type": "disabled"},
},
```

A predefined agent is one you created earlier; it runs with its own model, system prompt, tools, MCP servers and skills. An inline agent is defined by the lead at delegation time and runs on the lead's model and tools, so turning `inline_agents` off is how you keep every delegated task on the agents you chose. With inline agents off, the matching `predefined_agents` list needs at least one entry, or the request fails with a 400.

A list entry takes one of four forms: the agent ID as a string, `{"type": "agent", "id": ...}`, the same with a `version` to pin it, or `{"type": "self"}` for copies of the lead itself. References are snapshotted when the lead is created or updated, so a later change to the reader reaches the lead only through an update that sends the list again. The older `coordinator` type still exists for a roster alone, with the entries under `agents`.

Three rules shape every roster:

- **One level only.** An agent that has `multiagent` set cannot appear in another agent's lists; trying it fails with a 400 validation error.
- **25 child threads at a time.** Idle threads count until you archive them; advisor threads and a workflow run's threads do not.
- **One inference geography.** The lead and every listed agent pin the same `inference_geo`, or none of them pins one.

## Threads: One Sandbox, Separate Contexts

All agents in a session share the sandbox, its filesystem and its vault credentials, and each one works in its own session thread with its own conversation history. A subagent sees none of the lead's conversation, so every delegated task has to carry the paths, constraints and report format the subagent needs. Threads persist: the lead can send a follow-up to a subagent it called earlier, and that subagent still has its previous turns.

The session-level stream is the primary thread. It shows the lead's own work plus a condensed view of the others: when a thread starts, what the lead sent it, what came back, and anything that blocks on your client.

| Event on the primary stream | Meaning |
|---|---|
| `session.thread_created` | A thread started; carries `session_thread_id` and `agent_name` |
| `session.thread_status_running` | A thread began work |
| `session.thread_status_idle` | A thread waits for input; carries a `stop_reason` |
| `session.thread_status_terminated` | A thread was archived or failed and accepts no more input |
| `agent.thread_message_sent` | The lead sent a subagent a task or a follow-up |
| `agent.thread_message_received` | A subagent sent the lead a report or a question |

To see one agent's full reasoning and tool calls, list or stream its thread directly:

```python
for thread in client.beta.sessions.threads.list(session.id):
    print(f"[{thread.agent.name}] {thread.status}")

for event in client.beta.sessions.threads.events.list(thread.id, session_id=session.id):
    print(f"[{event.type}] {event.processed_at}")
```

A subagent's tool confirmation or custom tool call is cross-posted to the primary thread with a `session_thread_id`, so one stream is all your client watches. You answer with `user.tool_confirmation` or `user.custom_tool_result` exactly as in [topic 07](../07-agent-human-in-the-loop/readme.md#two-gates-not-one), and the server routes the reply by its ID.

## Dynamic Workflows and the Advisor

A roster suits a handful of well-scoped tasks. For work with more pieces than 25 threads can hold, such as reviewing hundreds of documents, a dynamic workflow lets the agent write a program that runs many agents in phases and combines their results; the server executes it in the background as a workflow run. There is no API call that starts a run: you describe the work in a `user.message`, and a line in the agent's system prompt says which tasks justify one, because every agent in a run consumes tokens.

The advisor gives the primary thread a stronger model to consult while it keeps doing the work itself, for planning an approach or reviewing a draft before finishing. Set `advisor` to `{"type": "enabled", "model": "claude-opus-5-5"}`; the agent's own model must not be more capable than its advisor, and consultations are billed at the advisor's rates. Claude Opus 5.5 returns redacted advice, so your client sees a `[{"type": "redacted"}]` placeholder while the agent reads the full text server-side.

## Outcomes: Define Done and Let a Grader Check It

An outcome turns a session from a conversation into a job with an acceptance test. You send a `user.define_outcome` event with a description and a rubric, and the agent starts working on receipt; no `user.message` is needed. The harness provisions a grader with its own context window, so the agent's implementation choices cannot talk the grader into a pass.

```python
outcome = {
    "type": "user.define_outcome",
    "description": "Write this week's customer feedback digest from the three regional files.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}
client.beta.sessions.events.send(session.id, events=[outcome])
```

| Field | Notes |
|---|---|
| `description` | The task the agent works toward |
| `rubric` | Required: `{"type": "text", "content": ...}` inline, or `{"type": "file", "file_id": ...}` uploaded once and reused |
| `max_iterations` | Optional: default 3, maximum 20 |

Each grading cycle emits `span.outcome_evaluation_start`, heartbeat `span.outcome_evaluation_ongoing` events, and a `span.outcome_evaluation_end` whose `result` decides what happens next.

| `result` | Next |
|---|---|
| `satisfied` | The session goes idle |
| `needs_revision` | The agent starts another iteration, guided by the grader's `explanation` |
| `max_iterations_reached` | One final acknowledgment turn, then idle; no further evaluation |
| `failed` | The session goes idle; the rubric does not apply to the deliverable, for example when it contradicts the description |
| `interrupted` | A `user.interrupt` arrived while the outcome was active |

Write criteria the grader can check one at a time ("the table has a Mentions column") and avoid impressions ("the digest reads well"). Only one outcome runs at a time; chain the next one after the previous `span.outcome_evaluation_end`, and the session keeps its history. The deliverable lands in `/mnt/session/outputs/`, where the Files API lists it with the session ID as `scope_id`, as in [topic 04](../04-agent-sessions-streaming/readme.md).

## Memory Stores: What Survives the Session

A memory store is a workspace-scoped collection of small text documents that outlives any session. Its API uses its own beta header, `agent-memory-2026-07-22`; sending it together with `managed-agents-2026-04-01` on a memory store request returns a 400, while attaching a store to a session stays a session call under the Managed Agents header. The SDK picks the right header for each namespace, so the header only matters when you build requests by hand.

```python
store = client.beta.memory_stores.create(
    name="Report Style",
    description="House style for the weekly feedback digest, plus lessons earlier runs recorded.",
)
client.beta.memory_stores.memories.create(store.id, path="/style-guide.md", content=STYLE_GUIDE)

session = client.beta.sessions.create(
    agent=lead.id,
    environment_id=environment.id,
    resources=[
        {
            "type": "memory_store",
            "memory_store_id": store.id,
            "access": "read_write",
            "instructions": "Read style-guide.md before writing. Read lessons.md if it exists.",
        }
    ],
)
```

Each attached store is mounted under `/mnt/memory/`, in a directory named after the store's display name as a lowercase slug, so "Report Style" becomes `/mnt/memory/report-style/`. Read the exact path from the `mount_path` of the session's memory-store resource. The agent uses its ordinary file tools on the mount, and a note naming each store, its path, access mode, description and instructions is added to its system prompt automatically.

| Limit | Value |
|---|---|
| Stores per session | 8 |
| Memories per store | 10,000 |
| Size of one memory | 100 kB, about 25k tokens |
| `instructions` per attachment | 4,096 characters |
| When a store can be attached | At session creation only |

`access` defaults to `read_write`; `read_only` is enforced at the filesystem level. A store an agent can write to is also a store a prompt injection can write to, and later sessions read that content as trusted memory, so attach reference material read-only.

Every change to a memory creates an immutable memory version (`memver_...`). A write the agent makes through the mount is attributed to the session, and `memory_versions.list()` shows it with a `created_by` of type `session_actor`. Versions are kept for 30 days, the recent versions of a live memory are kept regardless of age, and `memory_versions.redact()` scrubs content from an old version while keeping the audit trail.

## One Budget for Every Thread

A multiagent session multiplies spend, so cap it when you create it. The `budget` field takes `{"type": "limit", "max_list_cost": {"amount": "500", "currency": "USD"}}`, where `amount` is a whole number of US cents written as a string; a budget cannot be added to a session that was created without one.

The cap is shared by every thread, each thread is priced at its own model's list rate, and advisor consultations count against it too. When the total reaches the cap, threads pause and the session goes idle with `stop_reason` `budget_reached`; raising or removing the budget resumes the paused work.

## Hands-On Demo

[Turn One Agent into a Graded Team with Memory](demo-feedback-digest.md) starts from a single agent that reads three regional feedback files, then adds a reader subagent on Claude Haiku 5.5, a rubric the grader checks, a memory store with the house style, and a budget for the whole session.

## Hands-On Lab

[Review Code with Specialist Subagents, a Rubric and Team Memory](../../../labs/10-sdk-managed-agents/lab-04-agent-review-team-memory.md) builds a code review team: two read-only reviewer subagents, a lead that merges their findings against a rubric, a read-only conventions store and a read-write review history that a second session recalls.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/context` | Watch one local session's context fill as it reads every file itself, the cost a subagent's isolated thread takes off the lead |
| `/tasks` | Follow Claude Code's own background subagents finishing, the local counterpart of a session's child threads |
| `/workflows` | Open the progress view of a local workflow run, the counterpart of a dynamic workflow run's phases |
| `/memory` | Edit `CLAUDE.md` and auto memory, the local counterpart of a memory store that every new session reads |

## Key Topics covered in this module

- [Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration): the `multiagent` block, predefined and inline agents, workflows and the advisor
- [Session threads](https://platform.claude.com/docs/en/managed-agents/session-threads): listing, streaming, interrupting and archiving threads, and cross-posted tool calls
- [Workflow runs](https://platform.claude.com/docs/en/managed-agents/workflow-runs): run events, phases, interrupts and limits
- [Define outcomes](https://platform.claude.com/docs/en/managed-agents/define-outcomes): rubrics, the grader, evaluation events and retrieving deliverables
- [Using agent memory](https://platform.claude.com/docs/en/managed-agents/memory): stores, mounts, access modes, versions and redaction
- [Session budgets](https://platform.claude.com/docs/en/managed-agents/budgets): the shared spend cap and what happens at `budget_reached`
