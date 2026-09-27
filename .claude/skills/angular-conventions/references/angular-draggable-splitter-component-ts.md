# Splitter component TS

## Component TS (the essential shape)

```ts
@Component({
  selector: 'ux-splitter',
  templateUrl: './splitter.component.html',
  styleUrl: './splitter.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '[style.--ux-splitter-right]': 'rightWidthPx()' },
})
export class SplitterComponent {
  private readonly elementRef = inject(ElementRef<HTMLElement>);

  readonly storageKey = input.required<string>();   // one key per usage site
  readonly initial = input(320);
  readonly min = input(200);
  readonly max = input(560);
  readonly step = input(16);                         // px per Arrow key

  // Seeded from localStorage (clamped) yet freely settable by drag/keys.
  protected readonly rightWidth = linkedSignal<number>(() => this.readInitialWidth());
  protected readonly rightWidthPx = computed(() => `${this.rightWidth()}px`);
  protected readonly dragging = signal(false);

  constructor() {
    effect(() => {
      const key = this.storageKey();
      const width = this.rightWidth();
      if (!key || typeof window === 'undefined') return;
      try { window.localStorage.setItem(key, String(width)); } catch { /* storage disabled */ }
    });
  }

  protected onPointerDown(e: PointerEvent): void {
    (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
    this.dragging.set(true);
    e.preventDefault();
  }
  protected onPointerMove(e: PointerEvent): void {
    if (!this.dragging()) return;
    const rect = this.elementRef.nativeElement.getBoundingClientRect();
    this.rightWidth.set(this.clamp(rect.right - e.clientX, this.min(), this.max()));
  }
  protected onPointerUp(e: PointerEvent): void {
    if (!this.dragging()) return;
    this.dragging.set(false);
    const el = e.currentTarget as HTMLElement;
    if (el.hasPointerCapture?.(e.pointerId)) el.releasePointerCapture(e.pointerId);
  }

  protected growRight(): void  { this.rightWidth.update(w => this.clamp(w + this.step(), this.min(), this.max())); }
  protected shrinkRight(): void { this.rightWidth.update(w => this.clamp(w - this.step(), this.min(), this.max())); }

  private readInitialWidth(): number {
    const fallback = this.clamp(this.initial(), this.min(), this.max());
    if (typeof window === 'undefined') return fallback;
    const key = this.storageKey();
    if (!key) return fallback;
    try {
      const raw = window.localStorage.getItem(key);
      if (raw === null) return fallback;
      const n = Number(raw);
      return Number.isFinite(n) ? this.clamp(n, this.min(), this.max()) : fallback;
    } catch { return fallback; }
  }
  private clamp(v: number, min: number, max: number): number { return Math.min(Math.max(v, min), max); }
}
```

Back to the index: [angular-draggable-splitter](angular-draggable-splitter.md)
