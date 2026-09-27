# Deprecation analysis and the anti-pattern registry

## Task E: Deprecation Analysis (after C and D)

### Task E: Deprecation Analysis (after C and D)

Cross-reference console warnings with the Angular breaking-changes log. Categorize by severity using the registry below.

**Anti-pattern registry:**

| Anti-pattern | Severity |
|---|---|
| `@Input()` / `@Output()` decorators instead of `input()` / `output()` | Critical |
| `*ngIf` / `*ngFor` / `*ngSwitch` instead of `@if` / `@for` / `@switch` | Critical |
| `standalone: true` explicitly set (redundant in v20+) | High |
| `async pipe + Observable` for HTTP reads instead of `httpResource()` | High |
| `toSignal(http.get(...))` instead of `httpResource()` | High |
| `subscribe()` in component body | High |
| `BehaviorSubject` for local state instead of `signal()` | Medium |
| Constructor injection instead of `inject()` | Medium |
| `ChangeDetectionStrategy.Default` on components | Medium |
| `@HostBinding` / `@HostListener` instead of `host` object | Medium |
| `ngClass` / `ngStyle` instead of `[class.x]` / `[style.x]` bindings | Medium |
| Reactive Forms / `ngModel` where Signal Forms apply | Medium |

Back to the index: [angular-update](angular-update.md)
