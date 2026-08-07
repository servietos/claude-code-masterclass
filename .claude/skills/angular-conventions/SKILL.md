---
name: angular-conventions
description: Consolidated Angular conventions for components, dependency injection, forms, HTTP, routing, signals, unit testing, anti-patterns, MSAL authentication, and version upgrades. Use when working on Angular applications and you need modern Angular guidance or routing into a specific Angular concern. Triggers on component creation, inject(), signal forms, httpResource(), guards, route configuration, computed(), linkedSignal(), Vitest unit tests, legacy decorator cleanup, MSAL, Azure Entra, Angular architecture, and ng update to the latest Angular version.
---

# Angular Conventions

Group reusable Angular guidance under one entry skill.

## When to Use This Skill

- The task is Angular-specific but not yet narrowed to one Angular topic.
- You need a single entry point for Angular components, DI, forms, HTTP, routing, or signals.
- The repository has its own Angular rules in `docs/` and you want to pair those with general Angular conventions.

## Defaults

| Topic                       | Current rule                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| Angular version             | Angular `22.x` or later                                                                    |
| Architecture                | Standalone components — do NOT set `standalone: true` (default since v20)                 |
| Change detection            | `ChangeDetectionStrategy.OnPush` on every component                                       |
| Dependency injection        | `inject()` function only — never constructor parameters                                    |
| Inputs / Outputs            | `input()` / `output()` signals — never `@Input()` / `@Output()` decorators                |
| Host bindings               | `host` object in `@Component` / `@Directive` — never `@HostBinding` / `@HostListener`    |
| Template control flow       | `@if` / `@for` / `@switch` — never `*ngIf` / `*ngFor` / `*ngSwitch`                      |
| Class and style bindings    | `[class.x]` / `[style.x]` — never `ngClass` / `ngStyle`                                  |
| Local state                 | `signal()` — never `BehaviorSubject`                                                       |
| HTTP reads                  | `httpResource()` for reactive reads; `HttpClient` for mutations                            |
| Forms                       | Signal Forms (`form()` + `[formField]`) — never Reactive Forms or `ngModel`               |
| Scaffolding                 | Angular CLI for components, services, directives, and pipes                                |
| Project structure           | Feature-based folder organization; flat feature folders for smaller apps                   |
| Routing                     | `app.routes.ts` with functional guards and lazy-loaded feature routes                     |
| Component file layout       | Separate `.ts`, `.html`, `.css` files; kebab-case names; one folder per component         |

## Usage Note

- This skill captures shared Angular 22 conventions. Always check the target repository's own `docs/` or `CLAUDE.md` for repo-specific overrides (API base URLs, store architecture, auth provider, money conventions, etc.) before applying these defaults.

## Component File Organization

Angular projects use a functional storage hierarchy:

```
app/
  <feature>/              ← domain/feature folder (auth, person, cart, …)
    <component-name>/     ← one folder per component
      <component-name>.ts
      <component-name>.html  (if separate template)
      <component-name>.spec.ts
    <service>.ts          ← services live at feature level, not in a sub-folder
  shared/                 ← cross-cutting UI components used across features
    <shared-component>/
  store/                  ← global state (NgRx store, signal stores)
```

Rules:

- Each component gets its own folder named after the component.
- Files inside the folder share the component's name (e.g., `user-card/user-card.ts`).
- Services are placed at the feature level, not inside a component sub-folder.
- `shared/` contains components reused across multiple features.
- `store/` contains global state artifacts.

## Delegate Map

| Request type                                          | Reference to use                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------ |
| Build or refactor standalone components               | [`angular-component`](references/angular-component.md)             |
| Component folder layout and file organization         | [`angular-component`](references/angular-component.md)             |
| Configure dependency injection or providers           | [`angular-di`](references/angular-di.md)                           |
| Build forms and validation flows                      | [`angular-forms`](references/angular-forms.md)                     |
| Implement API calls and data loading                  | [`angular-http`](references/angular-http.md)                       |
| Configure navigation and route behavior               | [`angular-routing`](references/angular-routing.md)                 |
| Model reactive state with signals                     | [`angular-signals`](references/angular-signals.md)                 |
| Write unit tests with Vitest                          | [`angular-testing`](references/angular-testing.md)                 |
| Spot or fix anti-patterns / legacy code               | [`angular-antipatterns`](references/angular-antipatterns.md)       |
| MSAL authentication: v5 breaking changes, interaction-type rule, 401 triage | [`angular-msal-auth`](references/angular-msal-auth.md) |
| Upgrade or update an Angular app to the latest version | [`angular-update`](references/angular-update.md) |

## Example Prompts

- "Use angular-conventions to choose the right pattern for a new Angular form."
- "Route this Angular data-loading task to the right conventions reference."
- "Use angular-conventions for a component and signals refactor."
- "Use angular-conventions to scaffold a standalone Angular component and confirm the right CLI command."
- "Use angular-conventions to add a functional guard and lazy-loaded feature route."
- "Use angular-conventions to write Vitest unit tests for this component."
- "Use angular-conventions to find and fix legacy decorator anti-patterns in this file."
- "Use angular-conventions to wire MSAL sign-in and triage a 401 from the API."
- "Use angular-conventions to upgrade this workspace to the latest Angular version."

## Layout Rules

| Rule | Detail |
| ---- | ------ |
| Button alignment | All button groups (`.actions`, `.section-actions`, `.hero-actions`) must use `justify-content: flex-end` so buttons sit at the right edge |
| Default button style | Orange fill (`var(--accent)`) with black text (`#0a0c10`), `font-weight: 700`. This is the global default — no extra class needed |
| Destructive buttons | Stop, Delete, Remove, Drop — use `.btn-danger`: solid red fill (`var(--danger)`) with black text (`#0a0c10`) |
| Exceptions | Icon/utility buttons (`.btn-close`, `.tree-btn`, `.template-card`) keep their own component-scoped overrides |


## Repository Defaults

| Topic             | Current rule                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------ |
| Angular version   | Angular `21.x` or later                                                                    |
| Architecture      | Prefer standalone components                                                               |
| Scaffolding       | Use Angular CLI for components, services, directives, and pipes                            |
| Project structure | Use feature-based folder organization for larger Angular apps                              |
| Routing           | Use route configuration that fits the project, including `app.routes.ts` where appropriate |


## Project-Specific Rule

- Use this skill for reusable Angular guidance.
- Check the repository's `docs/` for project-specific architecture, folder layout, naming, and build rules before applying these conventions.


## Code Generation

Use Angular CLI rather than hand-writing the initial file structure.

```bash
ng generate component my-component
ng generate service my-service
ng generate directive my-directive
ng generate pipe my-pipe
```


## Development Commands

| Command            | Use                                        |
| ------------------ | ------------------------------------------ |
| `ng serve`         | Start the local Angular development server |
| `ng build`         | Create a production build                  |
| `ng build --watch` | Rebuild continuously during development    |


## Deployment Note

Angular projects in this repository are typically deployed to Azure Static Web Apps or Azure Container Apps. Use the project-specific deployment scripts and documentation instead of inventing a new deployment path.

## NDJSON Streaming into Signal Store

When a store feature must consume a server-sent NDJSON stream:

1. Use `fetch` (not `HttpClient`) to POST and obtain `response.body.getReader()`.
2. Decode chunks with `new TextDecoder()` in streaming mode; split on `\n`; parse each non-empty line as JSON.
3. Drive `patchState` for each event type (`stage`, `cost`, `result`) as lines arrive.
4. Fall back to an `HttpClient` call on any `fetch` rejection, non-200 response, or absent body.
5. Put the fallback in a separate async function and call it from both the `catch` block and the non-ok guard.
6. Revoke any object-URL (`URL.revokeObjectURL`) in both success and error paths.

Reference implementation: `src/inventory-ui/src/app/store/features/with-scan.feature.ts` (`resolvePhotoStream`).

