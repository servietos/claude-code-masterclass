# cli-utils

Two tiny string utilities used as the target project for Lab 01 of module 06 (headless mode and parallel worktrees).

| Utility | Source | Description |
|---|---|---|
| `slugify(input)` | `src/slugify.ts` | Lowercases the input, replaces every run of non-alphanumerics with a hyphen, and trims leading and trailing hyphens. |
| `kebabToCamel(input)` | `src/kebab-to-camel.ts` | Splits on hyphens and upper-cases the first letter of every segment after the first. |

## Run the tests

```bash
npm install
npm test
npm run typecheck
```

Vitest runs the two suites in `test/` directly against the TypeScript sources; no build step is needed. Because Vitest transpiles without type-checking, `npm run typecheck` (`tsc --noEmit`) is what actually enforces the strict `tsconfig.json`.
