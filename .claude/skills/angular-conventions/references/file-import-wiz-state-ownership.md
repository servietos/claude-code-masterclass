# Import wizard state ownership: component signals vs AppStore slice

## Architecture at a glance

| Concern | Where it lives |
|---|---|
| Step machine, selected line, view toggles | **local `signal()`s** in the wizard component |
| Draft, samples, busy flag, assistant messages, saved id | **AppStore slice** (surface store signals directly) |
| File → draft, chat, commit | **`rxMethod`s on the store**, calling the API — never client-side parsing |
| Review/mapping UI | **reuse the feature's normal edit components** bound to the draft's row array |
| Wizard shell | native modal (`role="dialog" aria-modal`), ESC to close, focus-trapped |

Key rule: **the component holds only view state; all import *data* lives in the store.** The wizard surfaces `store.importDraft()`, `store.importBusy()`, etc. directly, and mutates the draft through one `applyDraftPatch(partial)` store method (immutable patch). No client-side xlsx/pdf/csv library — the file is shipped as `FormData` and the API returns a full editable draft DTO.

Back to the index: [file-import-wiz](file-import-wiz.md)
