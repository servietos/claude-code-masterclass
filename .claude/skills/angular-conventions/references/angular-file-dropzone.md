# Angular File Drop Zone

A reusable, standalone **file drop zone** for the maintenance-planner UI (`src/ui`) — the entry control for every AI file-ingest automation (home chat, automations page, reservation attachments). Pattern distilled from `vouchers-ai/src/vouchers-ui` (`shared/file-upload/`) and adapted to this repo's Angular 22 + `@ngrx/signals` AppStore + bico-brand stack.

**The drop target is a `<button>`, not a `<div>`.**

| You want to... | Read |
| --- | --- |
| Should I use a drop zone here, and why is it a button with one dragging signal rather than a div? | [design](angular-file-dropzone-design.md) |
| What does the FileDropzone component and its template actually look like: inputs, output, emit(), drag handlers? | [component](angular-file-dropzone-component.md) |
| How do I style the zone with bico-brand tokens, or express the drag states inline in a Tailwind-utility app with no component CSS? | [styling](angular-file-dropzone-styling.md) |
| How does the host feature consume filesSelected and push the file into the signal store? | [host-wiring](angular-file-dropzone-host-wiring.md) |
| The drop zone lives in a shared shell and must route to whichever feature is active: how do I fire a store event instead of an output? | [global-drop-event](angular-file-dropzone-global-drop-event.md) |
| Is my drop zone implementation complete and correct, and where do the related upload, store and brand skills live? | [checklist](angular-file-dropzone-checklist.md) |
