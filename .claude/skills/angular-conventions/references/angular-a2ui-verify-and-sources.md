# Confirmed Versus Unverified APIs

## Verify Before Use

These APIs were drawn from community samples (ANGULARarchitects) and may differ in the installed package version. Confirm against the actual `@a2ui/angular` / `@a2ui/web_core` build:

- `minimalCatalog` vs `inject(BasicCatalog)` export form.
- `BASIC_FUNCTIONS` export name.

Confirmed against the installed package (no longer "verify," these are facts as of this project's `@a2ui/angular`/`@a2ui/web_core` versions):

- There is no `binding()` helper. Use `DynamicStringSchema` / `DynamicNumberSchema` / `DynamicBooleanSchema` / `DynamicStringListSchema`, exported directly from `@a2ui/web_core/v0_9` (`schema/common-types.d.ts`).
- `BasicCatalogBase` exists and is the correct class for custom catalog extension; its constructor merges `DEFAULT_COMPONENT_IMPLEMENTATIONS` with `options.extraComponents`, it does not replace the defaults.
- `AngularComponentImplementation` type exists and is exported from `@a2ui/angular/v0_9`. The `as unknown as AngularComponentImplementation` cast is still commonly required in practice — not because the type itself is wrong, but because a custom Zod schema built with the app's own `zod` install can structurally mismatch the `zod` nested inside `@a2ui/web_core` (see "Large Option Sets Need a Custom Compact Component" above).

## Sources

- A2UI home and spec: <https://a2ui.org/> , <https://a2ui.org/specification/v0.9-a2ui/>
- Client setup, catalogs, actions, theming guides: <https://a2ui.org/guides/client-setup/> , <https://a2ui.org/concepts/catalogs/> , <https://a2ui.org/concepts/actions/> , <https://a2ui.org/guides/theming/>
- GitHub: <https://github.com/a2ui-project/a2ui>
- Google Developers Blog: <https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/>
- Angular Blog (Devin Chasanoff): <https://blog.angular.dev/demystifying-a2ui-how-to-make-ai-agents-speak-ui-in-your-app-e1ffea2303bd>
- ANGULARarchitects A2UI series: <https://www.angulararchitects.io/en/blog/a2ui-how-ai-generates-dynamic-uis-at-runtime/>

Back to the index: [angular-a2ui](angular-a2ui.md)
