---
presents: demo-feedback-digest.md
budget: 4 min
beats: 3
---

# Present: Turn One Agent into a Graded Team with Memory

One session, three features: a lead that delegates reading to a cheaper subagent, an outcome a separate grader checks, and a memory store that is still there after the session is deleted. Three beats: delegation as a field on the agent, one stream for every thread, and an outcome in place of the prompt.

------

**Shell:** in PowerShell set the reuse ID with `$env:FEEDBACK_MEMORY_STORE_ID = "memstore_..."`; `export` fails there.

## Beats

### Beat 1: delegation is a field on the agent, and the session stays unchanged (1.5 min)

**Open:** [`feedback-digest-solution/01-feedback-digest.py`](feedback-digest-solution/01-feedback-digest.py) · the lead's `agents.create()` call · [The Multiagent Block on the Agent](readme.md#the-multiagent-block-on-the-agent)
**Say:** Who may delegate to whom is part of the agent's definition, versioned with it, so every session of that agent gets the same team. Listing the reader and switching inline agents off keeps the bulk reading on a model you priced.

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

**Result:** not executed: needs a valid ANTHROPIC_API_KEY
**Gotcha:** `workflows` defaults to enabled on `multiagent_20261001`; leave it out and the lead may start workflow runs that bill every agent in them.

### Beat 2: one stream carries every thread's start, task and report (1 min)

**Open:** [`feedback-digest-solution/01-feedback-digest.py`](feedback-digest-solution/01-feedback-digest.py) · the event loop · [Threads: One Sandbox, Separate Contexts](readme.md#threads-one-sandbox-separate-contexts)
**Say:** Each subagent works in its own thread with its own history, and the primary stream shows the handoffs between them. The task text is the only context a subagent gets, which is why the lead's prompt names paths.

```python
        elif event.type == "session.thread_created":
            print(f"[thread] {event.agent_name} {event.session_thread_id}")
        elif event.type == "agent.thread_message_sent":
            print(f"[task -> {event.to_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "agent.thread_message_received":
            print(f"[report <- {event.from_agent_name}] {text_of(event.content)[:100]}")
```

**Result:** not executed: needs a valid ANTHROPIC_API_KEY
**Gotcha:** `_sent` and `_received` are named from the stream they appear on; the same task is `received` on the reader's own thread stream.

### Beat 3: an outcome replaces the prompt, and a grader decides done (1.5 min)

**Open:** [`feedback-digest/digest.py`](feedback-digest/digest.py) beside [`feedback-digest-solution/01-feedback-digest.py`](feedback-digest-solution/01-feedback-digest.py) · the kickoff · [Outcomes: Define Done and Let a Grader Check It](readme.md#outcomes-define-done-and-let-a-grader-check-it)
**Say:** A prompt says what to do; a rubric also says what finished looks like, criterion by criterion. The grader reads the deliverable in its own context, so the agent's reasoning about its draft never reaches the verdict.

```python
outcome = {
    "type": "user.define_outcome",
    "description": "Write this week's customer feedback digest from the three regional files.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}
```

**Result:** not executed: needs a valid ANTHROPIC_API_KEY
**Gotcha:** send the outcome alone; the agent starts on receipt, and the idle check stays the loop's exit because `needs_revision` keeps the session running.

## If the room asks

| Question | Answer |
|---|---|
| Why does the reader run on Claude Haiku 5.5? | Reading is many input tokens and little reasoning; a listed agent runs and bills at its own model's rates. |
| Can the reader delegate further? | No: delegation is one level deep, and listing an agent that has `multiagent` set is a 400. |
| What stops the grader looping forever? | `max_iterations`, default 3 and at most 20, then one acknowledgment turn and idle. |
