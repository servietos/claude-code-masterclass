# Modernize Angular with the Angular MCP

Use the Angular MCP to evaluate and progressively modernize the food-shop-ng application with signal patterns, OnPush change detection, and zoneless architecture.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/04-mcp/01-using/food-shop-ng
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `food-shop-ng` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/04-mcp/01-using/food-shop-ng add ChangeDetectionStrategy.OnPush to every @Component decorator in src/app ....
```

That works for any step whose result is just files, such as the migrations in Steps 3 to 6. It does not work for the Angular MCP itself: `.mcp.json` loads from the directory the session was launched in, so a root session writes the server registration into the lab folder and then ignores it, leaving every MCP-driven prompt below without the tools it asks for. Launch inside the starter from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json` or `.mcp.json`, because both are read at startup.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session. You read them from the repo root without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Setup

The workspace runs Angular 21.1.4, which declares `engines.node = "^20.19.0 || ^22.12.0 || >=24.0.0"`. Any Node release inside that range works; Node 23.x does not. This lab was verified on Node 24.15.0 with npm 11.12.1.

The starter project is `labs/04-mcp/01-using/food-shop-ng`. The finished counterpart is `labs/04-mcp/01-using/food-shop-ng-solution`, which carries every change from Steps 3, 4 and 6 already applied; use it as the completed reference when you want to compare.

Open two terminals and navigate to `labs/04-mcp/01-using/food-shop-ng` in both. All commands below run unchanged in PowerShell and in git-bash.

In the first terminal, start the mock API. `db.json` ships two collections, `food` (the catalog the app reads on startup) and `orders`:

```bash
npx json-server@1 db.json --port 5000
```

The version is pinned because the bare `json-server` tag currently resolves to a `1.0.0-beta` pre-release, and an unpinned `npx` call prompts for an install on a machine that has no copy cached. When the server is up, the banner lists `http://localhost:5000/food` and `http://localhost:5000/orders`.

Two things to know about this mock API:

- Nothing else may hold port 5000. The repo's own .NET catalog service in `src/food-app/catalog-api` binds the same port and serves a different food list, so a learner with that project running silently gets the wrong catalog.
- json-server v1 persists writes back into `db.json` and rewrites numeric ids as strings. Run `git checkout db.json` to reset the file after any experiment that posts or puts.

In the second terminal, install dependencies and start the Angular dev server:

```bash
npm install
npm start
```

Open [http://localhost:4200](http://localhost:4200) in a browser and navigate to the catalog. The table should render seven items from the mock API. Checkout is mocked, so no orders backend is required.

---

## Setup: Register the Angular MCP

Create a `.mcp.json` file in `labs/04-mcp/01-using/food-shop-ng`, the same folder you launched Claude Code in, with the Angular MCP server:

```json
{
  "mcpServers": {
    "angular": {
      "command": "npx",
      "args": ["-y", "@angular/cli", "mcp"]
    }
  }
}
```

The Angular MCP documentation is at [https://angular.dev/ai/mcp](https://angular.dev/ai/mcp).

You created `.mcp.json` after the session started, so Claude Code has not read it yet: restart with `/exit` then `claude` in the same folder, and confirm the server with `/mcp`. Then run `/init` to let Claude Code read the codebase, and use the following prompt to refine the context:

```text
This is an Angular food shop application. I want to modernize it step by step using the Angular MCP. The app uses Zone.js, NgRx, Angular Material, and MSAL auth. Auth is currently disabled in the development environment.
```

---

## Step 1: Evaluate Modernization Opportunities

**Overview:** Before making any changes, get a structured picture of where the codebase stands against current Angular best practices. The Angular MCP can read the project and surface gaps across versions, change detection, signal readiness, and Zone.js usage. This assessment drives the plan for all subsequent steps.

**Research / Planning / Discussion:**

```text
Read the files in this Angular project and describe the current architecture: which version of Angular and NgRx are installed, what change detection strategies are in use, and what input/output patterns you see across the components. Do not make any changes yet.
```

**Finding:** A good response names the exact Angular and NgRx versions from `package.json`, identifies which components are missing `changeDetection`, lists every `@Input()` and `@Output()` decorator and which files they appear in, and notes whether Zone.js is present. It should also get the bootstrap story right: `src/main.ts` calls `bootstrapApplication(AppComponent, appConfig)`, so `src/app/app.config.ts` is the live bootstrap, `src/app/food/food.module.ts` is a lazy-loaded feature NgModule reached through `loadChildren` in `app.routes.ts`, and `src/app/app-routing.module.ts` is dead code that nothing imports. If Claude reports `app-routing.module.ts` as the app's routing setup, correct it before moving on, otherwise later steps get applied to a file that is not in the running app. If Claude only gives a high-level summary without citing specific files, ask it to go deeper.

**Recipe:**

```text
Use the Angular MCP tools to analyze this project and produce a modernization report. For each area below, describe the current state found in the code and the recommended migration path:

1. Angular and NgRx package versions
2. Change detection strategy across components
3. @Input() and @Output() usage, signal inputs and outputs opportunity
4. Reactive forms, signal-based forms opportunity
5. Zone.js usage and zoneless readiness

List the files that need changes for each area.
```

**Expected Outcome:** Claude produces a report covering all five areas. Across `src/app` it finds 17 `@Component` decorators, 7 `@Input()` declarations and 7 `@Output()` declarations. It identifies `food-list.component.ts` (one `@Input() food` plus three `@Output()`s) and `food-edit.component.ts` (`@Input() food` plus `@Output() saveFood`) as candidates for signal inputs and outputs, `app.config.ts` as the target for the zoneless provider, and `food-edit.component.ts` as the candidate for signal-based forms.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Upgrade Angular Packages

**Overview:** The workspace is one major version behind, not several. It ships `@angular/core` and `@angular/cli` at 21.1.4, `@angular/material` at 21.1.4 and `@ngrx/store` at 21.0.1, against 22.0.8, 22.0.6 and 21.1.1 respectively at the time of writing. Angular 21 already provides `input()`, `output()`, `provideZonelessChangeDetection()` and the experimental signal forms API, so Steps 3 to 6 all run on the shipped versions and none of them require this upgrade. Treat this step as deliberate practice with `ng update` and the Angular MCP rather than a prerequisite.

**Research / Planning / Discussion:**

```text
What Angular and NgRx packages are installed in this project? How far behind are they from the latest available versions, and what is the recommended upgrade sequence for Angular?
```

**Finding:** A good response shows the current version of `@angular/core`, `@angular/cli` and the `@ngrx` packages alongside their latest available versions, and it should get the distance right: Angular is one major behind (21.x to 22.x) and NgRx is one minor behind (21.0.1 to 21.1.1), not several majors. It should also state the general Angular rule that upgrades go one major version at a time and that `@angular/core` and `@angular/cli` go before NgRx, without implying this repo needs a multi-major chain. If Claude claims the current versions block signal APIs or zoneless, push back: both are available in Angular 21. If Claude does not use the Angular MCP, ask it to consult the MCP before proceeding.

**Recipe:**

```text
Using the Angular MCP, check which Angular and NgRx packages have available upgrades. Report the version distance first. Then run ng update to move the workspace forward one major version at a time, starting with @angular/core and @angular/cli, then @angular/material, then the @ngrx packages. Apply any automatic migrations offered by the schematics. If there are breaking changes in the source code, fix them. After upgrading, confirm the app builds with npm run build.
```

**Expected Outcome:** `package.json` shows updated Angular and NgRx version numbers. The app compiles without errors. The Angular MCP reports the workspace is on the latest available versions.

> This step is optional. Steps 3 to 6 were all verified on the shipped Angular 21.1.4 without it, so you can skip ahead and come back to the upgrade later.

---

## Step 3: Apply OnPush Change Detection

**Overview:** The default change detection strategy checks every component on every browser event, which creates unnecessary work in a component-heavy application. Adding `ChangeDetectionStrategy.OnPush` to every component tells Angular to only check when inputs change or a signal emits, reducing re-render overhead significantly.

**Research / Planning / Discussion:**

```text
Read the components in src/app. Which ones are missing a changeDetection property in their @Component decorator? Why does OnPush matter for a component-heavy application like this one?
```

**Finding:** A good response lists each component file and states whether it has `changeDetection` set. The correct answer here is that all 17 components are missing it: not a single file in `src/app` sets `changeDetection` today. It should explain that without OnPush, Angular traverses the entire component tree on every change detection cycle and that OnPush limits checks to components with changed inputs or signal emissions. If Claude gives a general explanation but does not enumerate the files, ask it to check each file explicitly.

**Recipe:**

```text
Use the Angular MCP to confirm that OnPush is the recommended default change detection strategy for standalone components in the current Angular version. Then add `changeDetection: ChangeDetectionStrategy.OnPush` to every @Component decorator in src/app that does not already have it. Import ChangeDetectionStrategy from @angular/core where needed. Run npm run build to confirm there are no compile errors.
```

**Expected Outcome:** All 17 `@Component` decorators in `src/app` include `changeDetection: ChangeDetectionStrategy.OnPush`. `npm run build` exits 0 and the app renders the food list correctly in the browser.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Convert to Signal Inputs and Outputs

**Overview:** The `@Input()` and `@Output()` decorators predate Angular's reactivity model. Replacing them with `input()` and `output()` integrates component bindings into the signal graph, enabling computed values that automatically re-derive when inputs change and removing the need for `ngOnChanges`.

**Research / Planning / Discussion:**

```text
Read the components in src/app and identify every @Input() and @Output() decorator. Which components use ngOnChanges, and what does each ngOnChanges do? I want to understand the scope before changing anything.
```

**Finding:** A good response names every component that declares `@Input()` or `@Output()`, all 7 of each, and lists which inputs each `ngOnChanges` reacts to. For `food-list.component.ts` and `food-edit.component.ts`, Claude should identify the specific inputs involved and note whether the `ngOnChanges` logic can be replaced by `computed()` or `effect()`. If it only lists file names without describing what each hook does, push back and ask for more detail.

**Recipe:**

```text
Use the Angular MCP to get the current Angular recommendation for signal inputs and outputs. The mechanical part can run as schematics: ng generate @angular/core:signal-input-migration and ng generate @angular/core:output-migration. Then replace any ngOnChanges lifecycle hooks that only react to input changes with computed() or effect() as appropriate, and update all parent templates that bind to these inputs and outputs.

One known breaking case: src/app/food/shop/checkout/checkout-form/checkout-form.component.ts declares `@Input({ required: true }) order: Order = new Order();` and builds its FormBuilder group at field-initialization time from this.order(). Converting that to input.required<Order>() drops the initializer and the build fails with NG8118, "`order` is a required `input` and does not have a value in this context". Either keep the default with `readonly order = input<Order>(new Order());` or move the form construction into an effect or linkedSignal so it runs after the input is bound.

Run npm run build and confirm the app works in the browser.
```

**Expected Outcome:** No `@Input()` or `@Output()` decorators remain in `src/app`. The two schematics report 7 of 7 inputs and 7 of 7 outputs migrated. `food-list.component.ts` and `food-edit.component.ts` use `input()` for their inputs and `output()` for their event emitters, `ngOnChanges` is gone from components where it only reacted to input changes, and `npm run build` exits 0 after the `checkout-form.component.ts` fix.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 5: Migrate to Signal-Based Forms

**Overview:** `FormBuilder` and `FormGroup` are imperative APIs that sit outside the signal graph. The signal-based forms API connects form state directly to Angular's reactivity model, so form values and validity become signals that other computed values can depend on without subscribing to observables. In Angular 21 this API is experimental and lives in its own entry point, `@angular/forms/signals`, so expect the surface to change between releases. There is no migration schematic for it either, which makes this step hand-written work rather than a mechanical conversion.

**Research / Planning / Discussion:**

```text
Read src/app/food/catalog/food-edit/food-edit.component.ts and explain how the form is currently structured. Then describe the signal-based forms API exported from @angular/forms/signals in the installed Angular version, its stability level, and how it differs from FormBuilder and FormGroup.
```

**Finding:** A good response describes the existing `FormGroup` structure in `food-edit.component.ts`, names the controls and their validators, `name: [Validators.required, Validators.minLength(3)]` and `inStock: [Validators.required, Validators.min(1)]`, and then explains what the signal-based API replaces (observable-based `valueChanges`, `FormBuilder.group()`, and imperative `.value` reads). It should also flag that the API is marked experimental in the installed version. If Claude describes the new API without reading the existing component first, or presents it as stable, ask it to read the file and check the entry point before continuing.

**Recipe:**

```text
The file src/app/food/catalog/food-edit/food-edit.component.ts uses FormBuilder and FormGroup to manage a reactive form. Use the Angular MCP to look up the recommended signal-based forms API from the @angular/forms/signals entry point for the current Angular version and migrate this component to use it. Update food-edit.component.html to match the new API. Keep the existing validation rules (name: required + minLength(3), inStock: required + min(1)). Run npm run build, then verify in the browser that the validation messages still appear and that the component emits its save output with the edited data.
```

**Expected Outcome:** `food-edit.component.ts` no longer imports `FormBuilder` or `FormGroup`. The form uses the signal-based forms API from `@angular/forms/signals`. Validation messages appear correctly and saving a food item still triggers the output event with the correct data.

> Do not verify this step by expecting a successful save round trip against json-server. `FoodDataService.update()` PUTs to `${catalogApi}/food` because the real .NET API has that signature, while json-server only accepts `PUT /food/:id`, so `PUT /food` answers 404. `POST /food` does work, so the add path is the one to click through against the mock. For a full save round trip, run the repo's .NET catalog service from `src/food-app/catalog-api` on port 5000 instead of json-server.

---

## Step 6: Remove Zone.js (Zoneless)

**Overview:** Zone.js patches browser APIs to trigger change detection automatically, but it adds bundle weight and makes the timing of change detection opaque. The zoneless provider replaces it with explicit signal-driven updates, completing the migration to a fully reactive architecture.

**Research / Planning / Discussion:**

```text
Read src/app/app.config.ts and angular.json. Identify every place where Zone.js is referenced or configured, including both the build target and the test target. Then describe what the zoneless provider replaces and what risks exist if any components depended on automatic change detection from Zone.js.
```

**Finding:** A good response identifies `provideZoneChangeDetection({ eventCoalescing: true })` in `app.config.ts` and both `zone.js` entries in `angular.json`: the `polyfills` array of the build target, and the `polyfills` array of the karma test target, which lists `zone.js` and `zone.js/testing` for the 4 `.spec.ts` files in the workspace. It should note that components relying on automatic triggering from `setTimeout`, Promise resolution, or event handlers may need `markForCheck()` or signal-based state to keep the UI in sync after the switch. If Claude names only the build target or misses `app.config.ts`, ask it to read both files fully before proceeding.

**Recipe:**

```text
Use the Angular MCP to get the correct steps for migrating to zoneless change detection in the current Angular version. Then:

1. Replace provideZoneChangeDetection in src/app/app.config.ts with provideZonelessChangeDetection().
2. Remove zone.js from the polyfills array of the BUILD target in angular.json. Leave the test target alone for now.
3. Keep zone.js installed. The karma test target still lists zone.js and zone.js/testing in its own polyfills array, so removing the package while those entries remain leaves the 4 spec files unable to resolve their polyfills. Only drop the dependency if you also strip both entries from the test target polyfills in the same change.
4. Fix any components that relied on Zone.js for change detection by ensuring they use signals, the async pipe, or explicit markForCheck() where needed.

Run npm run build and then verify in the browser that the food list loads and cart interactions update the UI correctly.
```

**Expected Outcome:** `app.config.ts` uses `provideZonelessChangeDetection()`. The build target in `angular.json` no longer lists `zone.js`, and the polyfills chunk disappears from the build output. `npm run build` exits 0 and the app runs in the browser: the catalog and shop pages render, and cart quantity changes and form interactions update the UI without Zone.js.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.
