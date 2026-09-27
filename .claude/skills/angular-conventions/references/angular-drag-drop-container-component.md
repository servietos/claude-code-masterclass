# The drop-target container component

### Drop-target container (`drag-grid.ts`)

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  ElementRef,
  computed,
  signal,
  viewChild,
} from '@angular/core';
import { DraggableItem, type DragPoint } from './draggable-item/draggable-item';

interface CellId {
  row: number;
  col: string;
  blocked: boolean;
}

@Component({
  selector: 'app-drag-grid',
  imports: [DraggableItem],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './drag-grid.html',
  styleUrl: './drag-grid.css',
})
export class DragGrid {
  private static readonly EDGE_PX = 64;
  private static readonly SCROLL_STEP_PX = 14;

  protected readonly draggedItemId = signal<number | null>(null);
  protected readonly dragOverCell = signal<CellId | null>(null);
  protected readonly isDragging = signal(false);

  private readonly gridWrapper = viewChild<ElementRef<HTMLElement>>('gridWrapper');

  protected readonly dragOverValid = computed(() => {
    const cell = this.dragOverCell();
    return cell !== null && !cell.blocked;
  });

  protected onDragStarted(itemId: number): void {
    this.draggedItemId.set(itemId);
    this.isDragging.set(true);
  }

  protected onDragMoved(point: DragPoint): void {
    this.dragOverCell.set(this.cellAtPoint(point));
    this.autoScroll(point);
  }

  protected onDragDropped(point: DragPoint): void {
    const itemId = this.draggedItemId();
    const cell = this.cellAtPoint(point) ?? this.dragOverCell();
    this.dragOverCell.set(null);
    this.draggedItemId.set(null);
    this.isDragging.set(false);
    if (itemId === null || cell === null || cell.blocked) return;
    this.moveItem(itemId, cell);
  }

  private moveItem(itemId: number, cell: CellId): void {
    // Persist to the backend / store here (optimistic update).
  }

  /** pointer-events:none on card overlay wrappers lets this fall through to the cell. */
  private cellAtPoint(point: DragPoint): CellId | null {
    const el = document
      .elementsFromPoint(point.x, point.y)
      .find(
        (node): node is HTMLElement =>
          node instanceof HTMLElement && node.dataset['col'] != null,
      );
    if (!el) return null;
    const row = Number(el.dataset['row']);
    const col = el.dataset['col'] ?? '';
    if (!Number.isFinite(row) || !col) return null;
    return { row, col, blocked: el.dataset['blocked'] === 'true' };
  }

  private autoScroll(point: DragPoint): void {
    const wrapper = this.gridWrapper()?.nativeElement;
    if (!wrapper) return;
    const rect = wrapper.getBoundingClientRect();
    if (point.y < rect.top + DragGrid.EDGE_PX) {
      wrapper.scrollTop -= DragGrid.SCROLL_STEP_PX;
    } else if (point.y > rect.bottom - DragGrid.EDGE_PX) {
      wrapper.scrollTop += DragGrid.SCROLL_STEP_PX;
    }
  }

  protected isCellDragOver(row: number, col: string): boolean {
    const cell = this.dragOverCell();
    return cell?.row === row && cell?.col === col && !cell.blocked;
  }

  protected isCellDragOverInvalid(row: number, col: string): boolean {
    const cell = this.dragOverCell();
    return cell?.row === row && cell?.col === col && cell.blocked;
  }
}
```


Back to the index: [angular-drag-drop](angular-drag-drop.md)
