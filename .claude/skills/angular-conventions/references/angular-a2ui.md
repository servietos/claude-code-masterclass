# Angular A2UI

Rendering agent-authored declarative UI in an Angular client: the protocol, the client wiring, catalogs and custom components, actions, theming and the failure modes.

**Protocol status (as of June 2026):** v0.9.1 is stable/production. v1.0 is release candidate (adds `actionResponse`, action IDs, `surfaceProperties`). Import from `@a2ui/angular/v0_9` until v1.0 is declared stable.

| You want to... | Read |
|---|---|
| What is A2UI, which protocol version to import, and should this UI be generative at all? | [angular-a2ui-concepts](angular-a2ui-concepts.md) |
| What JSON does the agent emit? createSurface, updateComponents, updateDataModel, deleteSurface, and the path/call binding rules. | [angular-a2ui-messages](angular-a2ui-messages.md) |
| Installing the packages and providing A2UI_RENDERER_CONFIG; also NG0201 No provider found for MarkdownRenderer. | [angular-a2ui-setup](angular-a2ui-setup.md) |
| How do I put a surface on screen, track active surface IDs, feed agent messages, and unsubscribe from onAction? | [angular-a2ui-rendering](angular-a2ui-rendering.md) |
| Which components ship in BasicCatalog, and how do I register a CustomCatalog extending BasicCatalogBase? | [angular-a2ui-catalogs](angular-a2ui-catalogs.md) |
| How do I write the three files for a new component: Zod schema, Angular component, catalog entry, and keep them in correspondence? | [angular-a2ui-custom-component](angular-a2ui-custom-component.md) |
| ChoicePicker renders 30 radio buttons and there is no dropdown variant: build a Select, and template the agent prompt literally. | [angular-a2ui-large-option-sets](angular-a2ui-large-option-sets.md) |
| TS2344/TS2322 claiming your ZodObject is missing _type or _parse, or the browser still shows old code and Component type not found. | [angular-a2ui-zod-duplicate-install](angular-a2ui-zod-duplicate-install.md) |
| The user clicked a Button: how does the action reach my code, what shape is it, and how do I update optimistically? | [angular-a2ui-actions](angular-a2ui-actions.md) |
| How do I restyle rendered surfaces? The --a2ui-* CSS tokens, dark mode, and why agents never send colors. | [angular-a2ui-theming](angular-a2ui-theming.md) |
| Keeping Zod schema, agent prompt and Angular component in sync, and when a catalog change needs a new catalogId URI. | [angular-a2ui-schema-source-of-truth](angular-a2ui-schema-source-of-truth.md) |
| Components silently missing, bootstrap throwing on inject(), VALIDATION_FAILED, leaked subscriptions, mixed v0_9/v1_0 imports. | [angular-a2ui-gotchas](angular-a2ui-gotchas.md) |
| Which exports in this doc are confirmed against the installed package, which still need checking, and where it all came from. | [angular-a2ui-verify-and-sources](angular-a2ui-verify-and-sources.md) |
