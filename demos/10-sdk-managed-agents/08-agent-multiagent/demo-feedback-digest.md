# Turn One Agent into a Graded Team with Memory

One agent that reads every file, judges its own draft and forgets everything when the session ends is the setup most first prototypes ship with. You start from exactly that agent writing a weekly digest from three regional feedback files, then give it a reader subagent on a cheaper model, a rubric a separate grader checks, a memory store holding the house style, and one budget for the whole session.

------

Work in [`feedback-digest/`](feedback-digest/readme.md) after `pip install -r requirements.txt`; the finished result is beside it in [`feedback-digest-solution/`](feedback-digest-solution/01-feedback-digest.py).

## Step 1: Run the Single-Agent Baseline

The starter uploads `feedback/emea.csv`, `feedback/americas.csv` and `feedback/apac.csv`, mounts them under `/mnt/session/uploads/feedback/`, and asks one Claude Opus 5.5 agent for the digest with a plain message. Run `python digest.py`.

```python
prompt = "Write this week's customer feedback digest from the three regional files."

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
    )
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY. Keep the downloaded `outputs/feedback-digest.md` open, because nothing in this run told the agent what a good digest looks like.

## Step 2: Hand the Reading to a Cheaper Subagent

A Claude Haiku 5.5 `Feedback reader` with read-only tools (`read`, `glob`, `grep`) reads the three CSV files while the Opus lead keeps the merge. Create the reader before the lead, because the lead's `multiagent` block refers to it by `reader.id`:

```python
reader = client.beta.agents.create(
    name="Feedback reader",
    description="Reads one regional feedback CSV and reports its top themes with mention counts and ticket ids.",
    model="claude-haiku-5-5",
    system=(
        "Read only the CSV file you are pointed at. Report its three most frequent themes, "
        "each with the number of tickets that mention it and two example ticket ids. Report only; write no files."
    ),
    tools=[
        {
            "type": "agent_toolset_20260401",
            "default_config": {"enabled": False},
            "configs": [{"name": name, "enabled": True} for name in ("read", "glob", "grep")],
        }
    ],
)
```

Name the reader in the lead's `system` text, because the lead decides when to delegate. Add the `multiagent` block to the lead's `agents.create()` call:

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

The house style lives in a `Report Style` memory store, seeded from `STYLE_GUIDE` in the [solution](feedback-digest-solution/01-feedback-digest.py) and reused when `FEEDBACK_MEMORY_STORE_ID` is set. It attaches only when the session is created, next to the file mounts and one shared `budget`; `amount` is whole US cents as a string, so `"500"` caps the session at 5.00 USD.

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY. Turning `inline_agents` off keeps every task on the listed reader, and `workflows` is switched off by name because it defaults to enabled on this type.

## Step 3: Replace the Message with an Outcome

An outcome says what to do and when it is done, and the agent starts on receipt, so the `user.message` goes away and `RUBRIC` comes from the [solution](feedback-digest-solution/01-feedback-digest.py). The primary stream then carries a condensed view of every thread plus each grading cycle; add `text_of()` from the solution above the loop:

```python
outcome = {
    "type": "user.define_outcome",
    "description": "Write this week's customer feedback digest from the three regional files.",
    "rubric": {"type": "text", "content": RUBRIC},
    "max_iterations": 3,
}

with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(session.id, events=[outcome])
```

```python
        elif event.type == "session.thread_created":
            print(f"[thread] {event.agent_name} {event.session_thread_id}")
        elif event.type == "agent.thread_message_sent":
            print(f"[task -> {event.to_agent_name}] {text_of(event.content)[:100]}")
        elif event.type == "span.outcome_evaluation_end":
            print(f"[grader] iteration {event.iteration}: {event.result}")
            print(f"         {event.explanation}")
```

**Expected result:** not executed: needs a valid ANTHROPIC_API_KEY. A `needs_revision` result keeps the session running into the next iteration, so the loop ends on the idle that follows `satisfied`, `max_iterations_reached` or `failed`, or on `budget_reached`.
