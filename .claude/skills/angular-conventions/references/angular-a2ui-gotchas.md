# A2UI Anti-patterns

## Anti-patterns and Gotchas

**Schema drift.** If the Angular component and catalog Zod schema diverge, the renderer silently drops or misrenders components. Keep schema and component inputs in lockstep; bump the `catalogId` URI on any breaking change.

**Using `useValue` for `A2UI_RENDERER_CONFIG`.** `inject()` only works inside a factory or constructor context. Using `useValue: { catalogs: [inject(BasicCatalog)] }` throws at bootstrap. Always use `useFactory`.

**Forgetting `DestroyRef` cleanup.** `renderer.surfaceGroup.onAction` does not support `takeUntilDestroyed`. Always store the subscription and call `sub.unsubscribe()` inside `DestroyRef.onDestroy`.

**Hallucinated component names.** The agent can only use component types registered in the active catalog. Unknown type names produce `VALIDATION_FAILED` errors. Always include the full catalog schema (or a JSON Schema rendering of it) in the agent system prompt.

**`sendCatalogDescription: true` in production.** This flag sends the full catalog schema in every outgoing message. Useful for development; disable in production to reduce payload size and prevent prompt-injection attacks that exploit the schema description.

**Mixing version import paths.** `@a2ui/angular/v0_9` and `@a2ui/angular/v1_0` export differently-shaped types and token values. Never import from both in the same app until you are intentionally migrating.

**Arbitrary values in component properties.** A2UI is declarative. Never place raw HTML strings, JavaScript, or `<script>` tags in component property values. Agents must stay within catalog-defined primitives.

**Progressive rendering ordering.** Components start rendering as soon as a valid `root` component arrives, before all sibling `updateComponents` messages have been processed. Avoid sibling components that visually depend on each other's final dimensions when streaming is enabled.

Back to the index: [angular-a2ui](angular-a2ui.md)
