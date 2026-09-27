# Angular Signal Patterns

Signal-based patterns for Angular, one leaf per question. Carried from the full file: "The `resource()` API handles async data fetching with signals:"

| You want to... | Read |
| --- | --- |
| Fetching async data with resource(): status signals, defaultValue, reload/set/update, and skipping the load until a param exists. | [angular-signals-patterns-resource-api](angular-signals-patterns-resource-api.md) |
| How do I shape a root-provided store service: one private state signal, computed selectors, and async actions that update it? | [angular-signals-patterns-signal-store](angular-signals-patterns-signal-store.md) |
| Building form state out of signals: a createFormField factory with value, touched, dirty, computed errors and valid. | [angular-signals-patterns-form-state](angular-signals-patterns-form-state.md) |
| Async signal work: debouncing a query through toObservable/toSignal, and optimistic updates that roll back when the request fails. | [angular-signals-patterns-async-operations](angular-signals-patterns-async-operations.md) |
| Asserting on signals and computed values in a spec, setting up a store with HttpTestingController, or logging signal changes from an effect. | [angular-signals-patterns-testing-debugging](angular-signals-patterns-testing-debugging.md) |
