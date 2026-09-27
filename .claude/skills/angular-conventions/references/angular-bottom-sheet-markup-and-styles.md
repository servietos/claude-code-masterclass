# Bottom sheet template and stylesheet

### `x-bottom-sheet.component.html`

Reuse the app's shared dialog classes (titlebar / close / body) — only the outer
`<dialog>` and the drag handle are bottom-sheet-specific:

```html
<dialog
  #sheetEl
  class="x-bottom-sheet"
  [class.x-bottom-sheet--visible]="visible()"
  (close)="onDialogClosed()"
  (mousedown)="onBackdropClick($event)"
>
  <div class="x-bottom-sheet__handle" aria-hidden="true"></div>

  <div class="dialog__titlebar">
    <span class="dialog__title"><ng-content select="[sheet-title]" /></span>
    <button type="button" class="dialog__close" aria-label="Close" (click)="close()">✕</button>
  </div>

  <div class="dialog__body">
    <ng-content />
  </div>
</dialog>
```

### `x-bottom-sheet.component.scss`

```scss
// Bottom-sheet variant of the shared `.dialog` shell — reuses the app's
// `.dialog__titlebar`/`.dialog__title`/`.dialog__close`/`.dialog__body` classes
// verbatim; only the outer `<dialog>` geometry + transition differ from the
// centered dialog shell.
.x-bottom-sheet {
  box-sizing: border-box;
  position: fixed;
  inset: auto 0 0 0;
  width: 100%;
  max-width: none;
  max-height: min(80vh, 720px);
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transform: translateY(100%);
  transition: transform 200ms ease-out;

  // Scope to `&[open]`: `dialog:not([open]) { display: none }` is a UA rule that
  // an unconditional author `display` would incorrectly out-cascade.
  &[open] {
    display: flex;
    flex-direction: column;
  }

  &.x-bottom-sheet--visible {
    transform: translateY(0);
  }

  &::backdrop {
    background: rgba(28, 28, 28, 0.5);
  }

  @media (prefers-reduced-motion: reduce) {
    transition: none;
  }
}

.x-bottom-sheet__handle {
  flex: 0 0 auto;
  width: 36px;
  height: 4px;
  margin: 8px auto 0;
  border-radius: 2px;
  background: var(--divider-color, #d4d0c8);
}
```

Swap the hardcoded colors for the host design system's tokens (divider / scrim /
accent) when reusing.

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
