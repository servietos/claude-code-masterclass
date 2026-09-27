# Spec failures after the migration that are not defects

## Guard `matchMedia`

Replacing `BreakpointObserver` compiles and runs in the browser, then breaks every TestBed spec that
instantiates the service: the test DOM has no `matchMedia`. The same guard makes it SSR-safe.

```ts
constructor() {
  if (typeof window.matchMedia !== 'function') return;
  const query = window.matchMedia('(max-width: 959.98px)');
  ...
  inject(DestroyRef).onDestroy(() => query.removeEventListener('change', listener));
}
```

### Use the workspace's own test runner

In an `@angular/build` workspace the suite is wired by the `@angular/build:unit-test` builder
(`setupFiles`, the TestBed environment). `npx vitest run` bypasses all of it and reports a wall of
`Need to call TestBed.initTestEnvironment() first`, `localStorage is not defined`, or an unresolved
`templateUrl`. None of it is real. Run `npx ng test`. Check `angular.json` `architect.test.builder` before
believing a red suite, and say so in any agent brief: subagents fall into this too.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)
