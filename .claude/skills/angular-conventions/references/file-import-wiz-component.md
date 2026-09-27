# Import wizard component: the reference listing

## Reference implementation

`src/ui/src/app/<feature>/import-wizard/import-wizard.ts`

```ts
import { AfterViewInit, ChangeDetectionStrategy, Component, computed, effect, inject, input, output, signal } from '@angular/core';
import { AppStore } from '../../store/app.store';
import { FileDropzone } from '../../shared/file-dropzone/file-dropzone';

type Step = 1 | 2 | 3;

@Component({
  selector: 'app-import-wizard',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [FileDropzone /* , edit form/table, chat panel */],
  templateUrl: './import-wizard.html',
  styleUrl: './import-wizard.css',
})
export class ImportWizard implements AfterViewInit {
  initialFile = input<File | null>(null);   // pre-supplied (e.g. from a global drop)
  closed = output<void>();

  private store = inject(AppStore);

  // view state — local signals only
  protected step = signal<Step>(1);
  protected selectedIndex = signal(0);

  // import data — surfaced straight from the store
  protected draft   = this.store.importDraft;
  protected busy    = this.store.importBusy;
  protected samples = this.store.importSamples;
  protected messages = this.store.assistMessages;

  protected rows = computed(() => this.draft()?.Rows ?? []);
  protected selectedRow = computed(() => this.rows()[this.selectedIndex()] ?? null);

  private handledInitial: File | null = null;
  private ingested = signal(false);
  private accepting = signal(false);

  constructor() {
    // 1. auto-ingest a pre-supplied file exactly once
    effect(() => {
      const file = this.initialFile();
      if (file && file !== this.handledInitial && !this.ingested()) {
        this.handledInitial = file; this.ingested.set(true);
        this.store.ingestFile({ file, review: false });
      }
    });
    // 2. when a draft lands on step 1, advance to review
    effect(() => {
      if (this.draft() && this.step() === 1 && this.ingested()) { this.ingested.set(false); this.step.set(2); }
    });
    // 3. when the committed record gets an id, clear + close
    effect(() => {
      const id = this.store.lastImportedId();
      if (this.accepting() && id) { this.accepting.set(false); this.store.clearImport(); this.closed.emit(); }
    });
  }

  ngAfterViewInit() { /* focus the backdrop for ESC/trap */ }

  onFilesSelected(files: File[]) {
    const file = files[0];
    if (!file) return;
    this.ingested.set(true);
    this.store.ingestFile({ file, review: false });
  }

  next() { if (this.step() < 3) this.step.update(s => (s + 1) as Step); }
  goTo(s: Step) { this.step.set(s); }

  onRowChange(partial: Record<string, unknown>) {
    const current = this.draft(); if (!current) return;
    const idx = this.selectedIndex();
    const Rows = current.Rows.map((r, i) => i === idx ? { ...r, ...partial } : r);
    this.store.applyDraftPatch({ Rows });
  }

  accept() {                              // "Übernehmen": walk to step 3, then commit
    if (!this.draft() || this.busy()) return;
    if (this.step() < 3) { this.next(); return; }
    this.accepting.set(true);
    this.store.commitDraft();
  }

  close() { this.store.clearImport(); this.closed.emit(); }
}
```

Back to the index: [file-import-wiz](file-import-wiz.md)
