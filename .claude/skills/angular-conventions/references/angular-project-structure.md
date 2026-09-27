# Angular project and component file structure

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

## Project-Specific Rule


- Use this skill for reusable Angular guidance.
- Check the repository's `docs/` for project-specific architecture, folder layout, naming, and build rules before applying these conventions.

Back to the index: [angular-conventions](../SKILL.md)
