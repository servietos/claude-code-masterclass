# Testing drag with Vitest

## Testing (Vitest, behavior-level)

`jsdom` does not implement real hit-testing, so stub
`document.elementsFromPoint` rather than dispatching genuine `PointerEvent`s
into the DOM and expecting geometry to resolve:

```typescript
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('DragGrid', () => {
  beforeEach(() => {
    vi.stubGlobal('document', {
      ...document,
      elementsFromPoint: vi.fn(),
    });
  });

  it('does not resolve a cell when elementsFromPoint has no data-col element', () => {
    (document.elementsFromPoint as ReturnType<typeof vi.fn>).mockReturnValue([
      document.createElement('div'),
    ]);
    // call the component's onDragMoved / private cellAtPoint via the public
    // dragOverCell signal and assert it stays null
  });

  it('resolves row/col and blocked from a matching data-* element', () => {
    const cell = document.createElement('div');
    cell.dataset['row'] = '2';
    cell.dataset['col'] = 'wed';
    cell.dataset['blocked'] = 'true';
    (document.elementsFromPoint as ReturnType<typeof vi.fn>).mockReturnValue([cell]);
    // assert dragOverCell() === { row: 2, col: 'wed', blocked: true }
  });

  it('refuses to persist a drop onto a blocked cell', () => {
    // seed dragOverCell with blocked: true, call onDragDropped, assert the
    // store/persist method was never called
  });

  it('a disabled item never emits dragStarted', () => {
    // set disabled = true, simulate a pointerdown + pointermove past the
    // threshold, assert dragStarted was not emitted
  });

  it('a click below the movement threshold still emits edit', () => {
    // pointerdown then pointerup at the same coordinates; assert edit fires
    // and dragStarted does not
  });
});
```

Follow `angular-testing` conventions when extending — assert on emitted
outputs and public signals, not on internal event wiring.


Back to the index: [angular-drag-drop](angular-drag-drop.md)
