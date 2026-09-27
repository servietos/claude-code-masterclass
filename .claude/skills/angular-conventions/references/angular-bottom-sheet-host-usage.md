# Opening a bottom sheet from a host

### Usage from a host

```html
<!-- host.component.html -->
<app-x-bottom-sheet #sheet>
  <span sheet-title>Quick actions</span>
  <!-- any projected content -->
</app-x-bottom-sheet>

<button type="button" (click)="sheet().open()">Open</button>
```

```typescript
// host.component.ts
import { Component, viewChild } from '@angular/core';
import { XBottomSheetComponent } from '../shared/x-bottom-sheet/x-bottom-sheet.component';

@Component({
  selector: 'app-host',
  templateUrl: './host.component.html',
  imports: [XBottomSheetComponent],
})
export class HostComponent {
  protected readonly sheet = viewChild.required(XBottomSheetComponent);
}
```

Back to the index: [angular-bottom-sheet](angular-bottom-sheet.md)
