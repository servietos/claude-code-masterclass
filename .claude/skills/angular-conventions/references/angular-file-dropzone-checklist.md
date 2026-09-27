# File Drop Zone: Review Checklist

## Checklist

- [ ] Standalone, `OnPush`, signal inputs/outputs (no decorators).
- [ ] Drop target is a `<button>`; picker is a hidden `sr-only <input type="file">`.
- [ ] `preventDefault()` on `dragover`/`dragleave`/`drop`.
- [ ] Single `emit()` normalizes `dataTransfer.files` and `input.files`; `input.value=''` reset.
- [ ] `multiple` gate slices to `[files[0]]` when off.
- [ ] No store/HTTP/validation coupling inside the component — host wires `filesSelected` to the AppStore.
- [ ] Styling via bico-brand tokens; active state is a `[class.*-active]="dragging()"` binding.
- [ ] Vitest: assert `filesSelected` emits on drop and on change, respects `multiple`, and toggles `dragging`.

## Related

- [`file-import-wiz`](file-import-wiz.md) — the multi-step wizard the drop zone feeds.
- [`angular-http`](angular-http.md) — `rxMethod` + `FormData` upload to the API.
- [`angular-signal-store-design`](angular-signal-store-design.md) — where ingest state lives.
- `bico-brand` skill — the mustard-gold + charcoal tokens for the zone styling.

Back to the index: [angular-file-dropzone](angular-file-dropzone.md)
