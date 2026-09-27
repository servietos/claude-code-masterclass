# Removing Angular Material without leaving mimic CSS

## Removing Angular Material

Deleting `@angular/material` / `@angular/cdk` imports is necessary but **not sufficient** — component SCSS can still *reproduce* the Material look after the package is gone. When de-Materializing a component or app, also grep for and strip Material-mimic CSS:

| Mimic pattern | What it looks like |
|---|---|
| Elevation shadow | A `box-shadow` triple matching `0 3px 1px -2px rgba(...), 0 2px 2px 0 ..., 0 1px 5px 0 ...` (Material's elevation mixin output, hand-copied into plain CSS) |
| Material font | `font-family: Roboto` |
| Material tracking | `letter-spacing: 0.0892857143em` |

Teardown checklist:

1. `grep -rE "@angular/(material|cdk)" src` returns zero matches.
2. No `mat-`/`cdk-` markup remains in any template.
3. The Material theme import is gone from `styles.scss`.
4. No Material-mimic CSS (table above) remains in component styles.
5. Build is green.

For the full migration playbook (orchestration, the one-custom-component rule, verification
hygiene) see the `.claude/skills/tailwind-migration/` skill.

Back to the index: [angular-antipatterns](angular-antipatterns.md)
