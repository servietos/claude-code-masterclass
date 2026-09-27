# File Drop Zone: When to Use and Core Principles

## When to use

- Adding a "drag a file here or click to browse" control anywhere in `src/ui`.
- Wiring the home-chat or automations file-drop entry points (see `docs/ai-automations/readme.md`).
- You need drag-and-drop + click-to-browse with keyboard/a11y support and no external library.

## Core principles (why this shape)

1. **The drop target is a `<button>`, not a `<div>`.** You get focus, Enter/Space activation, and `aria-label` for free — no manual `tabindex`/`keydown` wiring.
2. **A hidden `<input type="file" class="sr-only">` is the real picker.** The button's click opens it via `viewChild`.
3. **One `dragging = signal(false)`** drives the active style through `[class.*-active]="dragging()"`. `dragover → true`, `dragleave`/`drop → false`. Every drag handler calls `event.preventDefault()` (without it the browser navigates to the dropped file).
4. **One private `emit(list: FileList | null)`** normalizes both sources (drop's `dataTransfer.files` and input's `input.files`): guard empty → `Array.from` → slice to `[files[0]]` unless `multiple` is set.
5. **Reset `input.value = ''` after selection** so re-picking the *same* file fires `change` again.
6. **The component is store- and HTTP-agnostic.** It emits `output<File[]>()` and nothing else. No type/size validation inside — `accept` only hints the native picker; real validation belongs to the host or the API. The host wires the emitted files to the AppStore.


Back to the index: [angular-file-dropzone](angular-file-dropzone.md)
