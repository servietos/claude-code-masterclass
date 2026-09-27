# Legacy syntax: DI, templates and component declaration

## Dependency Injection

| Wrong | Correct |
|---|---|
| `constructor(private svc: UserService)` | `svc = inject(UserService)` |
| `@Injectable({ providedIn: 'root' })` with constructor DI | Use `inject()` in field initializer |

## Templates

| Wrong | Correct |
|---|---|
| `*ngIf="condition"` | `@if (condition) { }` |
| `*ngFor="let x of list"` | `@for (x of list; track x.id) { }` |
| `*ngSwitch` | `@switch (val) { @case ('x') { } }` |
| `[ngClass]="{ active: flag }"` | `[class.active]="flag()"` |
| `[ngStyle]="{ color: val }"` | `[style.color]="val()"` |
| `@HostBinding` / `@HostListener` | `host: { '[class.x]': '...', '(click)': '...' }` |
| A scoped `--open` modifier class that silently fails to apply | Drive state-carrying properties with `[style.prop]` bindings — see `angular-disclosure-panels.md` |

## Architecture

| Wrong | Correct |
|---|---|
| `NgModule` for feature organization | Standalone imports |
| `import CommonModule` | Import specific directives/pipes |
| `standalone: true` in decorator | Omit — standalone is the default in v20+ |
| Default change detection on components | `ChangeDetectionStrategy.OnPush` |

Back to the index: [angular-antipatterns](angular-antipatterns.md)
