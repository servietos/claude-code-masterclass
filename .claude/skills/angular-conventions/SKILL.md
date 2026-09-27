---
name: angular-conventions
description: Angular 22+ conventions and the single entry point for Angular work: components, signals, DI with inject(), Signal Forms, httpResource(), routing and guards, NgRx Signal Store, directives, overlays and dialogs, MSAL auth, A2UI generative UI, Vitest testing, CSS that will not apply, data-table column geometry, bundle-size optimization, runtime config injection, drag-and-drop reordering, migrating off Angular Material to Tailwind v4, and file downloads. Use when the task is Angular-specific but not yet narrowed to one topic, or to route into a specific Angular concern. Triggers on remove angular material, material to tailwind, drop @angular/cdk, tailwind v4 angular, cannot apply unknown utility class, borders disappeared after tailwind, dialog not centered, migrate many apps to tailwind, roll out a shared app shell, uninstall @angular/cdk, @angular/aria peer dependency, cdk scrolling virtual scroll, TestBed.initTestEnvironment first, vitest reports mass failures, ng test vs vitest, fixed height overlaps content, Angular architecture, standalone component, inject(), signal(), computed(), signal forms, httpResource(), route guard, MSAL login does nothing, interaction_in_progress, duplicate HTTP requests, initial budget exceeded, css change has no effect, container query not working, table shifts on sort, column picker, empty aria-live gap, runtime config injection, reorder cards, download a file, TestBed, vi.mock, ng test.
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
| State management            | **NgRx Signal Store (`@ngrx/signals`) is required** for shared/server state — `signalStoreFeature()` slices with `withState`/`withComputed`/`withMethods`, async via `rxMethod` + `tapResponse` + `patchState`. `signal()` is for component-local UI state only; never `BehaviorSubject` stores or class-based `@ngrx/store` reducers. |
| HTTP reads                  | `httpResource()` for reactive reads; `HttpClient` for mutations                            |
| Forms                       | Signal Forms (`form()` + `[formField]`) — never Reactive Forms or `ngModel`               |
| Scaffolding                 | Angular CLI for components, services, directives, and pipes                                |
| Project structure           | Feature-based folder organization; flat feature folders for smaller apps                   |
| Routing                     | `app.routes.ts` with functional guards and lazy-loaded feature routes                     |
| Component file layout       | Separate `.ts`, `.html`, `.css` files; kebab-case names; one folder per component         |
| Component organization      | Functional hierarchy: feature folder → component sub-folder                                |

## Delegate Map


| Request type                                          | Reference to use                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------ |
| Build or refactor standalone components               | [`angular-component`](references/angular-component.md)             |
| Component folder layout and file organization         | [`angular-component`](references/angular-component.md)             |
| Configure dependency injection or providers           | [`angular-di`](references/angular-di.md)                           |
| Build forms and validation flows                      | [`angular-forms`](references/angular-forms.md)                     |
| Implement API calls and data loading                  | [`angular-http`](references/angular-http.md)                       |
| Download a file the API generates, with auth          | [`angular-file-download`](references/angular-file-download.md)     |
| Configure navigation and route behavior               | [`angular-routing`](references/angular-routing.md)                 |
| Model reactive state with signals                     | [`angular-signals`](references/angular-signals.md)                 |
| Design app state so one composed signal store fully serves the app (feature-per-domain, container/presenter binding) | [`angular-signal-store-design`](references/angular-signal-store-design.md) |
| Add a global store-driven activity indicator (HTTP request-counter + explicit AI-activity flag + interceptor + progress bar) | [`angular-activity-indicator`](references/angular-activity-indicator.md) |
| Load-once data loading with local CRUD sync (ensure*Loaded guards, in-flight dedupe/shareReplay, resolvers scoped to what a route reads, mutations patch the store instead of refetching, sessionStorage TTL cache, duplicate-request elimination) | [`angular-load-once-store`](references/angular-load-once-store.md) |
| Write a spec for a component, service, guard or signal with Vitest and `TestBed` | [`angular-testing`](references/angular-testing.md)                 |
| Run or scope a Vitest suite and read the result (`ng test` vs raw `npx vitest`, `--include` vs `--filter`, a run that skipped everything but shows no red, one broken spec failing the whole type-check, which failing file to fix first) | [`angular-test-execution`](references/angular-test-execution.md) |
| Measure coverage and rank the gaps (`@vitest/coverage-v8` not installed, where `coverage-summary.json` actually lands, a `.html` file at ~0% functions, missing `<name>.spec.ts` is not missing coverage) | [`angular-test-coverage`](references/angular-test-coverage.md) |
| The spec fails for a reason that is not the code under test: `vi.mock` factory traps (`__spreadValues is not a function`, mock is `undefined`, `is not a constructor`, `vi.hoisted`), `expectOne` finding no matching request when the URL has query params, flushing the wrong body type for a blob request, one leaked request cascading into dozens of failures | [`angular-test-doubles`](references/angular-test-doubles.md) |
| A plain-bound native `<select>` renders with nothing selected (no `ngModel`/`formField`): `[value]` on the select loses to the options' own bindings, put `[selected]` on the options | [`angular-select-binding`](references/angular-select-binding.md) |
| Build modals/dialogs/popups, ESC-to-close, dark native controls | [`angular-overlays`](references/angular-overlays.md)     |
| Build a draggable/resizable two-pane splitter (`ux-splitter`) | [`angular-draggable-splitter`](references/angular-draggable-splitter.md) |
| Stable data-table column geometry (columns jump when sorting, table shifts on sort/filter, `table-fixed` vs `table-auto`, columns overflow the container, last column pushed off-screen, unwanted horizontal scrollbar, server-side sort with infinite scroll, collapsible nav rail changes available width at a fixed viewport, container query instead of media query, sidebar expanded vs collapsed, iPad Pro 13 inch) | [`angular-table-column-layout`](references/angular-table-column-layout.md) |
| User-resizable table columns (drag column border, resize column width, column resize handle, drag fires the sort by mistake, flexible column collapses to a few px, persist column widths, stale stored widths override new defaults) | [`angular-table-column-resize`](references/angular-table-column-resize.md) |
| Show/hide table columns (column picker, "Spalten" dropdown, hide a column, hidden by default, column visibility, explicit choice vs responsive breakpoint, checkbox stays checked below breakpoint, cannot hide last column) | [`angular-table-column-visibility`](references/angular-table-column-visibility.md) |
| Drag and drop for grids or reorderable lists without a library (cdkDrag alternative, reorder rows, draggable grid, drop target, not-allowed drop) | [`angular-drag-drop`](references/angular-drag-drop.md) |
| Build a bottom sheet with no Angular Material/CDK (native `<dialog>`, viewport-anchored, slide-up, imperative open()/close()) | [`angular-bottom-sheet`](references/angular-bottom-sheet.md) |
| Build a file drop zone / drag-and-drop file upload (dragover state, hidden input, single vs multi, `filesSelected` output, store-event variant) | [`angular-file-dropzone`](references/angular-file-dropzone.md) |
| Build a multi-step file-import wizard (upload → review/column-map → AI-assist → commit; draft in the store, no client-side parsing) | [`file-import-wiz`](references/file-import-wiz.md) |
| Blob download or a retained-documents list (blob download, document list, file download, object URL, retained documents, import documents; `HttpClient` blob → `createObjectURL` → anchor click) | [`blob-document-list`](references/blob-document-list.md) |
| Build a user & permission admin UI (RBAC: admin-users, admin-permissions, user/roles dialogs) backed by mixed auth (Entra MSAL + local JWT), with `withAuth`/`withAdmin` signal-store slices, a local-first token interceptor, and an `adminGuard` — admin UI, permission matrix, roles screen, RBAC UI, local login form, adminEmails | [`angular-users-permissions-admin`](references/angular-users-permissions-admin.md) |
| Build a collapsible/expandable disclosure panel or accordion, especially inside an equal-height card grid (collapsed by default, show more, panel will not expand, cards same height, `0fr`/`1fr` row animation) | [`angular-disclosure-panels`](references/angular-disclosure-panels.md) |
| Give a set of pages one shared chrome: eyebrow + H1 hero, KPI band, routed tab nav; fix two stacked headlines ("double headline"), convert stacked sections into routed tabs, replace explanatory prose with KPI tiles, share CSS primitives without leaking through global `styles.css` | [`angular-page-chrome`](references/angular-page-chrome.md) |
| A CSS edit has no visible effect: diagnose via the CSSOM, a stale `ng serve` bundle, a `@container` rule that cannot match its own container, an unlayered global beating a Tailwind utility, a class living in another component's stylesheet, or a `font-weight` the loaded font file cannot honour (prove the face is variable via `fvar` before declaring a weight), or a production build whose inlined critical CSS is blocked by the app's own CSP so the deployed page ships completely unstyled; choose `flex-wrap` over a container query for "sits beside, else wraps below" | [`angular-css-not-applying`](references/angular-css-not-applying.md) |
| Data the SPA ships as static files under `public/` is readable without login (the route guard protects the route, not the file): how to check, why basic auth breaks the app's own `fetch()`, why the edge cannot validate an MSAL token, the `Sec-Fetch-Dest`/`Sec-Fetch-Site` nginx and Caddy mitigation, and its honest obscurity-grade limits | [`spa-static-data-exposure`](references/spa-static-data-exposure.md) |
| Unexplained vertical space in a `gap`-spaced column: an always-rendered but currently empty `aria-live` wrapper (or any conditionally-empty child) still eats a full gap — `empty:absolute` vs `empty:hidden`, and why `:empty` still matches through an `@if` anchor | [`angular-live-region-layout`](references/angular-live-region-layout.md) |
| Inspect the RUNNING app's DI graph or signal graph from the browser (which providers actually resolved, is the interceptor registered once, did MSAL_INSTANCE resolve, is zoneless really on, why does this effect re-run, `angular:di_graph`, `angular:signal_graph`, `devtoolstooldiscovery`, `list_3p_developer_tools`, `categoryExperimentalThirdParty`, converting circular structure to JSON) | [`angular-runtime-graph-inspection`](references/angular-runtime-graph-inspection.md) |
| Remove Angular Material (and `@angular/cdk`) and rebuild the UI on Tailwind v4: wiring and style order, the `* { border: 0 }` reset that silently kills every Tailwind border, `@apply` refusing custom classes and the `@utility` escape, preflight breaking native `<dialog>` centring, the Material-to-Tailwind replacement map, fill-height flex chains, guarding `matchMedia` after dropping `BreakpointObserver`, the e2e/doc/fixture sweep the build does not catch, and the axe regressions Material used to cover (contrast numbers included) | [`material-tailwind-migration`](references/material-tailwind-migration.md) (helper: `scripts/material-to-tailwind.sh --verify\|--wire`) |
| Spot or fix anti-patterns / legacy code               | [`angular-antipatterns`](references/angular-antipatterns.md)       |
| Wire MSAL providers: interaction-type rule, `environment` config, the providers factory, `protectedResourceMap` keys, `app.config.ts` registration | [`angular-msal-auth`](references/angular-msal-auth.md) |
| MSAL application patterns: a cached `AuthService`, functional guards in both directions, local-only vs full logout, one `authEnabled` flag across SPA and API | [`msal-auth-patterns`](references/msal-auth-patterns.md) |
| MSAL is wired but misbehaving: blank page when auth is enabled, redirect loop through Microsoft, missing `Authorization` header, 401 triage, popup failure, Easy Auth conflict, the Login button that silently does nothing (an unsubscribed `loginRedirect()` swallowing `interaction_in_progress`) | [`msal-troubleshooting`](references/msal-troubleshooting.md) |
| Which `@azure/msal-angular` major to run and what each hop broke: v4/v5/v6 API changes, where `navigateToLoginRequestUrl` moved, the removed-API grep checklist | [`msal-version-changes`](references/msal-version-changes.md) |
| MSAL client wiring deep-dive: provider setup, `APP_INITIALIZER`, `AuthStateService`, single-bootstrap rules, the migration checklist, and whether the COOP redirect-bridge page is needed at all | [`msal-angular`](references/msal-angular.md) |
| Entra app registration via Azure CLI: create from scratch, redirect URIs, platform types, `requestedAccessTokenVersion` and the pre-authorization chicken-and-egg | [`msal-angular-appreg`](references/msal-angular-appreg.md) |
| Upgrade or update an Angular app to the latest version, and the compatibility gate for deciding what NOT to bump (TypeScript peer range off `@angular/compiler-cli`, stable-with-unmet-peer vs an RC, README support matrices no tool can see, test-env majors, the Node engine floor and where it is actually pinned, why caret floors are the deployed version when the Dockerfile has no lockfile). Run the gate first with `node <this-skill>/scripts/angular-update-preflight.mjs --root <dir>` | [`angular-update`](references/angular-update.md) |
| Fix a failing production bundle-size budget: measure eager vs lazy chunks, non-ESM tree-shaking traps, raw-vs-gzip budgets, lazy-init a heavy lib via dynamic `import()` (reduce bundle, main.js too big, initial budget exceeded, tree-shaking, lazy load) | [`angular-bundle-optimization`](references/angular-bundle-optimization.md) |
| Decide whether to adopt a third-party library at all: is it maintained, is the Angular wrapper dead, how many kB does it really cost against the current budget, and will it round-trip our content (is library X worth it, which markdown/rich-text/chart/date library, npmjs.com returns 403, registry.npmjs.org, weekly downloads, last publish, ngx wrapper unmaintained, use the library directly, measure gzip with esbuild, WYSIWYG mangles shortcodes or raw HTML or front matter) | [`angular-dependency-evaluation`](references/angular-dependency-evaluation.md) |
| Move per-environment values out of the bundle so one build serves every environment: read `globalThis.__APP_CONFIG__` in `environment.ts` with `??` fallbacks, load `config.js` from `index.html`, and retire the per-slot `environment.<slot>.ts` + `fileReplacements` (runtime config injection, config.js, `__APP_CONFIG__`, apiBase baked into the bundle, one bundle many environments, environment.blue.ts, fileReplacements per slot, slot-agnostic image, promote by retag) | [`angular-runtime-config`](references/angular-runtime-config.md) |
| Migrate markdown-renderer into a split demo-container layout | [`angular-migrate-markdown`](references/angular-migrate-markdown.md) |
| Render agent-driven generative UI with the A2UI protocol (catalogs, surfaces, actions, theming) | [`angular-a2ui`](references/angular-a2ui.md) |
| Build a multi-step wizard / setup flow: full-width step-rail shell, phase-driven active/done states, two-column step body, copy-to-clipboard, real-data chip filters | [`angular-wizard`](references/angular-wizard.md) |
| Where a component's files live, and when the repo's own docs override these defaults. | [`angular-project-structure`](references/angular-project-structure.md) |
| Button alignment, the default and destructive button styles, and which buttons are exempt. | [`angular-layout-rules`](references/angular-layout-rules.md) |
| Scaffold with the CLI, serve, build, watch; where these apps deploy. | [`angular-cli-and-build`](references/angular-cli-and-build.md) |
| Consume a server-sent NDJSON stream in a store feature, with the HttpClient fallback. | [`angular-ndjson-signal-store`](references/angular-ndjson-signal-store.md) |
| Worked phrasings that route into this skill. | [`angular-example-prompts`](references/angular-example-prompts.md) |
