# Nested FormGroups and FormArray

## FormBuilder Patterns

### Nested FormGroups

```typescript
@Component({
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <input formControlName="name" placeholder="Name" />
      
      <div formGroupName="address">
        <input formControlName="street" placeholder="Street" />
        <input formControlName="city" placeholder="City" />
        <input formControlName="zip" placeholder="ZIP" />
      </div>
      
      <button type="submit">Submit</button>
    </form>
  `,
})
export class Profile {
  private fb = inject(NonNullableFormBuilder);
  
  form = this.fb.group({
    name: ['', Validators.required],
    address: this.fb.group({
      street: [''],
      city: ['', Validators.required],
      zip: ['', [Validators.required, Validators.pattern(/^\d{5}$/)]],
    }),
  });
}
```

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


Back to the index: [angular-forms](angular-forms.md)
