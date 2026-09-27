# Cut B: lazy-init a heavy eager library

## Cut B — Lazy-init a heavy eager library via dynamic `import()`

Heavy libs that a root-level service/component imports statically (App Insights, charting, editors,
PDF/Excel) land in `main.js` even when they aren't needed at first paint. Convert to lazy init:

1. Change the top-level value import to a **type-only** import so it's erased at build time:
   ```ts
   import type { ApplicationInsights } from '@microsoft/applicationinsights-web';
   ```
2. Keep the constructor synchronous; fire an async initializer without awaiting:
   ```ts
   constructor() { void this.init(); }

   private async init() {
     const { ApplicationInsights } = await import('@microsoft/applicationinsights-web');
     this.instance = new ApplicationInsights({ /* same config */ });
     this.instance.loadAppInsights();
     this.flushPending();
   }
   ```
3. **Queue-and-flush** every public method so calls made before init resolves are never dropped or
   thrown — route them through a helper that calls straight through once `this.instance` exists,
   else pushes a thunk onto a `pendingCalls` array flushed (in order) at the end of `init()`.

Result: the package moves into its own lazy async chunk (`applicationinsights-web-*.js`), off the
initial budget. Proven cut: ~170 kB off `main.js`. Verify with `--stats-json` that `main.js` now
contains only the `await import('./chunk-*.js')` call site, not the SDK's class code.

Which eager libs are safe to defer: anything whose first use is after first paint. Libs that must
run before route guards resolve (e.g. **MSAL** auth) are legitimately eager — don't defer those.

Back to the index: [angular-bundle-optimization](angular-bundle-optimization.md)
