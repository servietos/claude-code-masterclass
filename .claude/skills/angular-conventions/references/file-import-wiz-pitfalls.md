# Import wizard pitfalls and shipping checklist

## Pitfalls

- **Don't parse the file in the browser.** No xlsx/pdf/csv lib on the client — the API owns extraction so the AI/OCR and column-mapping logic live in one place.
- **Draft lives in the store, not the component** — otherwise the assistant step and the review step fight over two copies.
- **Guard the auto-ingest effect** with a `handledInitial` reference + `ingested` flag, or a re-render re-uploads the same file.
- **Zero ids on commit** server-side (`EMPTY_GUID` → insert); the client just posts the reviewed draft.
- **`applyDraftPatch` must be immutable** (`{ ...d, ...patch }`, `Rows.map(...)`) so OnPush + signals see the change.

## Checklist

- [ ] Standalone `OnPush`; `step = signal<1|2|3>()`; pill rail via `@for`, bodies via `@if`.
- [ ] All import data in the AppStore slice; component holds only view state.
- [ ] Three `effect()`s: auto-ingest-once, draft→advance, saved-id→close.
- [ ] Review step reuses existing edit form/table bound to `draft().Rows`; edits via `applyDraftPatch`.
- [ ] Optional assist step merges returned `PatchJson`.
- [ ] Both entry paths wired (explicit button + global drop).
- [ ] Vitest: draft advances the step, patch is immutable, commit emits `closed` on saved id.

Back to the index: [file-import-wiz](file-import-wiz.md)
