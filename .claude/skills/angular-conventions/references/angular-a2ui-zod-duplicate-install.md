# Two Zod Installs Break The Build

## Gotcha: two `zod` installs do not type-check against each other

### Gotcha: two `zod` installs do not type-check against each other

The app's own top-level `zod` and the `zod` nested inside `@a2ui/web_core/node_modules/zod` can be different major versions (v4 vs v3 in this project). A schema built with `z.object(...)` imported from the app's `zod` fails `CatalogComponent<typeof YourApi>`'s generic constraint and the `AngularComponentImplementation` assignment with a `TS2344`/`TS2322` error whose message oddly claims your `ZodObject` is "missing" properties like `_type`, `_parse`, `_getType` — that is two different `ZodType` classes, not a real schema mistake.

Symptom in dev: the Angular CLI build fails on the incremental rebuild, but the dev server keeps serving the last good bundle with no visible error in the browser — the page looks unchanged, and the browser console reports the *old* code's behavior (here, `A2uiRendererService` logged `Component type "Select" not found in catalog` because the catalog registration was never actually rebuilt). Check the terminal running `ng serve` for `✘ [ERROR] TS2344`/`TS2322` before assuming the browser or the DI wiring is wrong.

Fix: extend `CatalogComponent<any>` instead of `CatalogComponent<typeof YourApi>`, and cast the catalog entry with `... as unknown as AngularComponentImplementation` — exactly the cast this doc's "Defining a custom component" example already uses; now you know precisely why it is there.

Back to the index: [angular-a2ui](angular-a2ui.md)
