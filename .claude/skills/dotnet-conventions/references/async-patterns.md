## When to use

Writing or reviewing any `async`/`await` code: I/O calls, `Task`-returning methods, `ConfigureAwait`,
or async exception handling.

## Async/Await Patterns

- Use `async`/`await` for all I/O operations and long-running tasks.
- Return `Task` or `Task<T>` from async methods.
- Use `ConfigureAwait(false)` where appropriate.
- Handle async exceptions properly.

## An AsyncLocal set inside an awaited helper never reaches the caller

An `AsyncLocal<T>` value written inside an `async` method is restored when that method returns, so
the caller never sees it. This shape compiles, returns a disposable, and silently does nothing:

```csharp
using var scope = await BeginContextIfNoneActiveAsync();
await ai.CompleteAsync(messages);
```

`Current` is still `null` at the completion: the helper set the ambient context in its own execution
context, and the `await` handed the caller back its own. Open the scope in the caller instead: await
only the lookup, then call the synchronous `Begin` there.

```csharp
IDisposable agentScope = null;
if (AgentExecutionContext.Current == null)
{
    var (agentId, modelIds) = await AgentExecutionContext.ResolveJobContextAsync(ctx, JobName);
    agentScope = AgentExecutionContext.Begin(null, JobName, agentId, modelIds);
}
using var scope = agentScope;
```

Verify with a test whose fake completion captures `AgentExecutionContext.Current` and asserts it is
set. A test that only checks the disposable is not null passes against the broken helper.
