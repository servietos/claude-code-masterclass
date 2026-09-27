# The draggable source component

## Essential TS shape

### Draggable source (`draggable-item.ts`)

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  signal,
} from '@angular/core';

export interface DragPoint {
  x: number;
  y: number;
}

const DRAG_THRESHOLD_PX = 6;
const TOUCH_START_DELAY_MS = 160;

@Component({
  selector: 'app-draggable-item',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './draggable-item.html',
  styleUrl: './draggable-item.css',
  host: {
    '[class.is-dragging]': 'isDragging()',
    '[class.is-disabled]': 'disabled()',
    '[attr.data-item-id]': 'itemId()',
    '(pointerdown)': 'onPointerDown($event)',
    '(pointermove)': 'onPointerMove($event)',
    '(pointerup)': 'onPointerUp($event)',
    '(pointercancel)': 'onPointerCancel($event)',
    '(click)': 'onClick()',
    'style.touch-action': "'none'",
  },
})
export class DraggableItem {
  readonly itemId = input.required<number>();
  readonly disabled = input(false);
  readonly disabledReason = input<string | null>(null);

  readonly edit = output<number>();
  readonly dragStarted = output<number>();
  readonly dragMoved = output<DragPoint>();
  readonly dragDropped = output<DragPoint>();

  protected readonly isDragging = signal(false);

  private pointerId: number | null = null;
  private startPoint: DragPoint | null = null;
  private suppressClick = false;

  protected onPointerDown(event: PointerEvent): void {
    if (this.disabled()) return;
    this.pointerId = event.pointerId;
    this.startPoint = { x: event.clientX, y: event.clientY };
    this.suppressClick = false;
    (event.target as HTMLElement).setPointerCapture(event.pointerId);
  }

  protected onPointerMove(event: PointerEvent): void {
    if (this.pointerId !== event.pointerId || !this.startPoint) return;
    const point: DragPoint = { x: event.clientX, y: event.clientY };

    if (!this.isDragging()) {
      const dx = point.x - this.startPoint.x;
      const dy = point.y - this.startPoint.y;
      if (Math.hypot(dx, dy) < DRAG_THRESHOLD_PX) return;
      this.isDragging.set(true);
      this.suppressClick = true;
      this.dragStarted.emit(this.itemId());
    }

    event.preventDefault();
    this.dragMoved.emit(point);
  }

  protected onPointerUp(event: PointerEvent): void {
    if (this.pointerId !== event.pointerId) return;
    if (this.isDragging()) {
      this.dragDropped.emit({ x: event.clientX, y: event.clientY });
    }
    this.resetPointer(event.pointerId);
  }

  protected onPointerCancel(event: PointerEvent): void {
    if (this.pointerId !== event.pointerId) return;
    this.resetPointer(event.pointerId);
  }

  protected onClick(): void {
    if (this.suppressClick || this.disabled()) return;
    this.edit.emit(this.itemId());
  }

  private resetPointer(pointerId: number): void {
    this.isDragging.set(false);
    this.pointerId = null;
    this.startPoint = null;
  }
}
```

`dragStartDelay`-style touch behavior (press-and-hold before a drag engages, so
a swipe still scrolls) can be layered on top of this: start a
`setTimeout(TOUCH_START_DELAY_MS)` in `onPointerDown` for `event.pointerType ===
'touch'` that arms a `touchArmed` flag; gate `isDragging.set(true)` in
`onPointerMove` on that flag being set (immediately `true` for
`event.pointerType === 'mouse'`).


Back to the index: [angular-drag-drop](angular-drag-drop.md)
