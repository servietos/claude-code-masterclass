# Bottom sheet component class

## Minimal working example

### `x-bottom-sheet.component.ts`

```typescript
import { ChangeDetectionStrategy, Component, ElementRef, signal, viewChild } from '@angular/core';

/**
 * Generic bottom sheet shell — embed once per host (`<app-x-bottom-sheet #sheet>`)
 * and drive it imperatively via `open()`/`close()`:
 *
 *   <app-x-bottom-sheet #sheet>
 *     <span sheet-title>Quick actions</span>
 *     ...projected content...
 *   </app-x-bottom-sheet>
 *   ...
 *   this.sheet().open();
 */
@Component({
  selector: 'app-x-bottom-sheet',
  templateUrl: './x-bottom-sheet.component.html',
  styleUrls: ['./x-bottom-sheet.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class XBottomSheetComponent {
  private readonly dialogEl = viewChild<ElementRef<HTMLDialogElement>>('sheetEl');

  /** Drives the slide-up transition — false immediately after `showModal()`,
   * flipped true one frame later so the `transform` transition actually fires
   * (see "Entrance transition" above). */
  protected readonly visible = signal(false);

  private lastFocused: HTMLElement | null = null;

  open(): void {
    const el = this.dialogEl()?.nativeElement;
    if (!el || el.open) return;

    this.lastFocused = document.activeElement as HTMLElement | null;
    el.showModal();

    requestAnimationFrame(() => this.visible.set(true));
  }

  close(): void {
    const el = this.dialogEl()?.nativeElement;
    if (!el || !el.open) return;

    this.visible.set(false);
    // Let the slide-down transition play before the native close() removes
    // the dialog from the top layer — match the transition duration in the
    // stylesheet (200ms). Skip the wait if the user prefers reduced motion.
    const prefersReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    const delay = prefersReducedMotion ? 0 : 200;
    setTimeout(() => el.close(), delay);
  }

  /** Native `cancel` fires on Esc before `close`; add `preventDefault()` here
   * only if the host needs a "confirm before dismiss" guard. */
  protected onDialogClosed(): void {
    this.visible.set(false);
    this.lastFocused?.focus();
    this.lastFocused = null;
  }

  /** Closes on a backdrop click — `showModal()` puts click targets for the
   * backdrop itself on the `<dialog>` element (not a descendant), so comparing
   * `event.target` to the dialog element distinguishes a backdrop click from
   * a click inside the sheet content. */
  protected onBackdropClick(event: MouseEvent): void {
    if (event.target === this.dialogEl()?.nativeElement) {
      this.close();
    }
  }
}
```

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
