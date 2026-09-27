# File Drop Zone: Component TS and Template

## Reference implementation

`src/ui/src/app/shared/file-dropzone/file-dropzone.ts`

```ts
import { booleanAttribute, ChangeDetectionStrategy, Component, ElementRef, input, output, signal, viewChild } from '@angular/core';

@Component({
  selector: 'app-file-dropzone',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './file-dropzone.html',
  styleUrl: './file-dropzone.css',
})
export class FileDropzone {
  label = input<string>('');
  accept = input<string>('');                 // e.g. '.xlsx,.pdf,application/pdf'
  multiple = input(false, { transform: booleanAttribute });
  busy = input(false, { transform: booleanAttribute });
  progress = input<number | null>(null);

  filesSelected = output<File[]>();           // the ONLY output — host owns what happens next

  protected dragging = signal(false);
  private fileInput = viewChild.required<ElementRef<HTMLInputElement>>('fileInput');

  open() { this.fileInput().nativeElement.click(); }

  onSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    this.emit(input.files);
    input.value = '';                         // allow re-selecting the same file
  }

  onDragOver(event: DragEvent)  { event.preventDefault(); this.dragging.set(true); }
  onDragLeave(event: DragEvent) { event.preventDefault(); this.dragging.set(false); }
  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragging.set(false);
    this.emit(event.dataTransfer?.files ?? null);
  }

  private emit(list: FileList | null) {
    if (!list || list.length === 0) return;
    const files = Array.from(list);
    this.filesSelected.emit(this.multiple() ? files : [files[0]]);
  }
}
```

`src/ui/src/app/shared/file-dropzone/file-dropzone.html`

```html
<button type="button" class="dz" [class.dz-active]="dragging()"
  [attr.aria-label]="label() ? label() + ' hochladen' : 'Datei hochladen'"
  (click)="open()"
  (dragover)="onDragOver($event)" (dragleave)="onDragLeave($event)" (drop)="onDrop($event)">
  <span class="mdi mdi-cloud-upload dz-icon" aria-hidden="true"></span>
  @if (label()) { <span class="dz-label">{{ label() }}</span> }
  <span class="dz-hint">Hierher ziehen oder klicken</span>
  @if (busy()) {
    <div class="dz-progress" role="progressbar" [attr.aria-valuenow]="progress() ?? 0">
      <div class="dz-progress-bar" [style.width.%]="progress() ?? 0"></div>
    </div>
  }
</button>
<input #fileInput type="file" class="sr-only"
  [accept]="accept()" [multiple]="multiple()" (change)="onSelect($event)" />
```

Back to the index: [angular-file-dropzone](angular-file-dropzone.md)
