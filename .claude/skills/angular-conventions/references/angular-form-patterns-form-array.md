# Dynamic Forms with FormArray

## Dynamic Forms with FormArray

```typescript
import { FormArray } from '@angular/forms';

@Component({
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form">
      <div formArrayName="items">
        @for (item of items.controls; track $index; let i = $index) {
          <div [formGroupName]="i">
            <input formControlName="product" placeholder="Product" />
            <input formControlName="quantity" type="number" />
            <button type="button" (click)="removeItem(i)">Remove</button>
          </div>
        }
      </div>
      <button type="button" (click)="addItem()">Add Item</button>
    </form>
  `,
})
export class Order {
  private fb = inject(NonNullableFormBuilder);
  
  form = this.fb.group({
    items: this.fb.array([this.createItem()]),
  });
  
  get items() {
    return this.form.controls.items;
  }
  
  createItem() {
    return this.fb.group({
      product: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(1)]],
    });
  }
  
  addItem() {
    this.items.push(this.createItem());
  }
  
  removeItem(index: number) {
    this.items.removeAt(index);
  }
}
```

Back to the index: [angular-form-patterns](angular-form-patterns.md)
