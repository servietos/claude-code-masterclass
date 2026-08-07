# agent-framework-workflow — Agent Workflow Authoring

## When to Use

- Adding a new agent to a WorkflowBuilder or MagenticBuilder pipeline
- Changing workflow topology (linear → branching, sequential → concurrent)
- Adding HITL (human-in-the-loop) gates
- Configuring retry/revision logic
- Wiring `SkillsProvider` for per-agent skills

## Workflow Patterns

### Sequential Chain (WorkflowBuilder)

```python
workflow = (
    WorkflowBuilder(
        name="OptimizeWorkflow",
        start_executor=writer,
        output_executors=[writer, reviewer],
    )
    .add_edge(writer, reviewer)
    .build()
)
```

### Dynamic Coordination (MagenticBuilder)

```python
workflow = MagenticBuilder(
    participants=[writer, translator],
    manager_agent=manager,
    max_round_count=5,
    max_stall_count=2,
).build()

agent = workflow.as_agent()
```

### Conditional Branching

```python
workflow = (
    WorkflowBuilder(...)
    .add_switch_case_edge_group(reviewer, [
        Case(condition=is_revise, target=writer),
        Default(target=publisher),
    ])
    .build()
)
```

### Adding a New Agent

1. Define the agent with `Agent(client, name=..., instructions=..., tools=..., context_providers=...)`
2. Add its skill directory under `skills/<agent-name>/`
3. Wire it into the builder with `.add_edge()`
4. Add to participants list (Magentic) or output_executors (Workflow)
5. If needed, update the operation router

## Example: content-creator-team

The content-creator uses `WorkflowBuilder` with an operation router that dispatches to optimize, translate, or create-article sub-flows. See `src/content-creator-team/main.py` for the full workflow topology.
