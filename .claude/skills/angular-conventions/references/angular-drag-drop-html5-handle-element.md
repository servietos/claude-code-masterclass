# The HTML5 drag handle element

### The handle element decides whether HTML5 drag works at all

`draggable="true"` on a `<button>` (or any form control) **does not start a drag
in Chrome**. The control swallows the drag gesture at `mousedown`, so
`dragstart` never fires from real mouse input and the feature is simply dead —
no console error, no warning, correct-looking markup.

```html
<!-- dead: Chrome never fires dragstart from a form control -->
<button type="button" class="grip" draggable="true" (dragstart)="onDragStart($event, i)">…</button>

<!-- works: non-form element, keyboard-accessible by hand -->
<span class="grip" draggable="true" role="button" tabindex="0"
      (dragstart)="onDragStart($event, i)" (dragend)="endDrag()"
      (keydown)="onHandleKeydown($event, i)">…</span>
```

The `role="button"` + `tabindex="0"` pair is not optional: the moment you stop
using `<button>` you own focusability, the accessible role, and the keyboard
path (arrow keys that move the item) yourself.

**This bug survives every test you are likely to write.** A synthetic
`element.dispatchEvent(new DragEvent('dragstart', {dataTransfer: new DataTransfer()}))`
fires the handler regardless of the element type, so Vitest specs, a
`chrome-devtools` `evaluate_script` probe, and a scripted end-to-end drag all
report success against a `<button>` handle that no user can drag. Synthetic
DragEvents prove the *handlers* are wired; they say nothing about whether the
browser will *originate* a drag. Verify origination by element type
(`grip.tagName !== 'BUTTON'`), or by dragging it by hand once.


Back to the index: [angular-drag-drop](angular-drag-drop.md)
