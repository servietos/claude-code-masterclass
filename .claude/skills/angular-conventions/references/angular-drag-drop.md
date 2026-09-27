# Angular Grid Drag-and-Drop (Pointer Events, No CDK)

Dragging cards onto grid cells and reordering list rows with native Pointer Events, no `@angular/cdk`.

| You want to... | Read |
| --- | --- |
| Know why no CDK, and where the worked example lives | [rationale](angular-drag-drop-rationale.md) |
| Write the draggable card: capture, threshold, click-vs-drag | [source component](angular-drag-drop-source-component.md) |
| Write the container: elementsFromPoint, validity, auto-scroll | [container component](angular-drag-drop-container-component.md) |
| Get the `data-*` keys, overlay pointer-events and highlights right | [markup and CSS](angular-drag-drop-markup-and-css.md) |
| Handle a disabled item and an occupied cell | [disabled and blocked](angular-drag-drop-disabled-and-blocked.md) |
| Rewrite and persist an `{id, order}[]` array | [reordering](angular-drag-drop-reordering.md) |
| Show *where* a dragged row lands | [reorder affordances](angular-drag-drop-reorder-affordances.md) |
| Fix `dragstart` never firing in Chrome | [HTML5 handle element](angular-drag-drop-html5-handle-element.md) |
| Put grips behind an edit toggle | [edit mode gate](angular-drag-drop-edit-mode-gate.md) |
| Write drag specs under jsdom | [testing](angular-drag-drop-testing.md) |
| Debug a stuck drag or a silent no-op drop | [gotchas](angular-drag-drop-gotchas.md) |

`draggable="true"` on a `<button>` (or any form control) **does not start a drag in Chrome**.
