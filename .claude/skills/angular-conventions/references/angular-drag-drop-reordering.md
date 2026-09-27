# Reordering a list

## Reordering a list

Rewrite the array locally, then persist the whole order:

```typescript
protected onReorder(draggedId: number, targetId: number | null): void {
  const current = [...this.items()];
  const dragged = current.find((i) => i.id === draggedId);
  if (!dragged) return;

  const withoutDragged = current.filter((i) => i.id !== draggedId);
  const insertIdx =
    targetId === null
      ? withoutDragged.length
      : Math.max(0, withoutDragged.findIndex((i) => i.id === targetId));
  withoutDragged.splice(insertIdx, 0, dragged);

  const ordered = withoutDragged.map((item, index) => ({ id: item.id, order: index }));
  this.items.set(withoutDragged); // optimistic local update
  this.store.reorderItems({ items: ordered }); // persist to the backend
}
```

`onReorder` can be wired to the same Pointer Events source/container pair
above (resolve the target row instead of a grid cell), or to plain
**HTML5 Drag and Drop** (`draggable="true"` + `(dragstart)`/`(dragover)`/
`(drop)`/`(dragend)`, tracking source/target ids and calling
`event.preventDefault()` in `dragover`) — the native API is simpler when the
only requirement is reordering siblings in one list, with no free 2D movement
and no custom grid-cell resolver needed.

**The reorder payload is idempotent, not self-inverting.** Persisting
`{id, order}[]` with *absolute* target indices means re-sending the same payload
sets the same indices again — it does **not** undo a previous move. To revert,
send the inverse mapping (or swap the two rows' current indices once); never
re-apply the same payload expecting it to toggle back.


Back to the index: [angular-drag-drop](angular-drag-drop.md)
