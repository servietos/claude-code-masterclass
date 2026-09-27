# Grid markup and drag CSS

## Template

```html
<div class="drag-grid-wrapper no-scrollbar" #gridWrapper>
  <div class="drag-grid" [class.drag-grid--dragging]="isDragging()">
    @for (row of rows; track row) {
      @for (col of cols; track col) {
        <div
          class="drag-grid__cell"
          [class.drag-grid__cell--drag-over]="isCellDragOver(row, col)"
          [class.drag-grid__cell--drag-over-invalid]="isCellDragOverInvalid(row, col)"
          [attr.data-row]="row"
          [attr.data-col]="col"
          [attr.data-blocked]="isCellOccupied(row, col)"
        ></div>
      }
    }

    @for (item of items(); track item.id) {
      <div class="drag-grid__anchor" [style.top]="anchorTop(item)">
        <app-draggable-item
          [itemId]="item.id"
          [disabled]="item.locked"
          [disabledReason]="item.locked ? 'Gesperrt durch Admin' : null"
          (edit)="openEdit($event)"
          (dragStarted)="onDragStarted($event)"
          (dragMoved)="onDragMoved($event)"
          (dragDropped)="onDragDropped($event)"
        />
      </div>
    }
  </div>
</div>
```

`data-row`/`data-col` identify the cell; `data-blocked` lets `cellAtPoint()`
read occupancy straight off the DOM without a second lookup into component
state. The anchor wrapper (`drag-grid__anchor`) must be `pointer-events: none`
in CSS — only `app-draggable-item` re-enables `pointer-events: all` — so
`elementsFromPoint` passes through it to the cell beneath.

## SCSS

```css
.drag-grid__cell {
  cursor: cell;
  transition: background 0.1s;
}

.drag-grid--dragging .drag-grid__cell {
  cursor: copy;
}

.drag-grid__cell--drag-over {
  background: color-mix(in srgb, var(--color-brand) 16%, transparent);
  box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--color-brand) 70%, transparent);
}

.drag-grid__cell--drag-over-invalid {
  background: color-mix(in srgb, var(--color-danger) 14%, transparent);
  box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--color-danger) 60%, transparent);
  cursor: not-allowed;
}

.drag-grid__anchor {
  position: absolute;
  pointer-events: none;
}

.drag-grid__anchor app-draggable-item {
  pointer-events: all;
  display: block;
}

app-draggable-item.is-dragging {
  opacity: 0.6;
  z-index: 3;
}

app-draggable-item.is-disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
```

Colors above use this repo's tokens (`--color-brand` gold, `--color-danger`);
swap in the host design system's accent/danger tokens when reusing the
pattern elsewhere.


Back to the index: [angular-drag-drop](angular-drag-drop.md)
