# State, data loading and test anti-patterns

## State Management

| Wrong | Correct |
|---|---|
| `BehaviorSubject` for local state | `signal()` |
| `Observable`-only state without signals | Combine with `toSignal()` or use `resource()` |
| `subscribe()` in component body | `toSignal()`, async pipe, or `resource()` |
| `@ngrx/store` class-based reducers | NgRx Signal Store (`withState`, `withMethods`) |

## Data Loading

| Wrong | Correct |
|---|---|
| Manual `http.get()` + `BehaviorSubject` wiring | `httpResource()` or `resource()` |
| `subscribe()` in `ngOnInit` for HTTP | `resource()` with declarative loader |

## Testing

| Wrong | Correct |
|---|---|
| Testing private methods | Test public behavior and outputs |
| Skipping error scenarios | Always test happy path + error + edge cases |
| No service mocking | Mock all external dependencies |
| `jasmine.createSpyObj` | `vi.fn()` (Vitest project uses Vitest APIs) |

Back to the index: [angular-antipatterns](angular-antipatterns.md)
