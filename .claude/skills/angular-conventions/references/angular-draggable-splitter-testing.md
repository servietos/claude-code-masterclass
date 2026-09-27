# Splitter tests

## Testing (Vitest, behavior-level)

Cover behavior, not pixels — set inputs / simulate keys, assert the width signal
and the ARIA attributes:

- clamps to `min` and `max` (drive `growRight`/`shrinkRight` past the bounds);
- restores a persisted value from `localStorage`, and **clamps an out-of-range
  persisted value** on read;
- persists on change (assert `localStorage.getItem(key)`);
- divider exposes `role="separator"` + `aria-valuemin/max/now`;
- Arrow Left/Right adjust and clamp.

## Tests

`splitter.component.spec.ts` — behavior-level Vitest: clamps to min/max both
directions, restores from `localStorage`, clamps an out-of-range persisted value,
persists on change, divider ARIA attributes, Arrow keys adjust + clamp. Follow
`angular-testing` conventions when extending.


Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)
