# Angular Component Patterns

Component-level recipes for Angular: two-way binding, view and content queries, injection and cross-component communication, lazy loading with `@defer`, attribute directives and error boundaries.

Default across all of them: use `inject()` function instead of constructor injection.

| You want to... | Read |
| --- | --- |
| Make a component support `[(value)]`: writing `model()`, `model.required()`, and the host input handler that sets it. | [angular-component-patterns-model-inputs](angular-component-patterns-model-inputs.md) |
| Get a handle on a child element, component, or projected content: `viewChild`/`viewChildren` and `contentChild`/`contentChildren`. | [angular-component-patterns-queries](angular-component-patterns-queries.md) |
| Let two components talk, and get a service into a component: `inject()` options, inputs down, outputs up, shared signal service. | [angular-component-patterns-injection-communication](angular-component-patterns-injection-communication.md) |
| Lazy-load a heavy component in the template: `@defer` with placeholder, loading and error blocks, and the full trigger list. | [angular-component-patterns-defer](angular-component-patterns-defer.md) |
| Write an aliased attribute directive with a host binding, or wrap content in a retryable error boundary. | [angular-component-patterns-directive-error-boundary](angular-component-patterns-directive-error-boundary.md) |
