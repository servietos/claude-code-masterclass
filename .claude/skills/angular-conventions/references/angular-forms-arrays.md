# Signal Form Arrays

## Arrays and Dynamic Fields

```typescript
interface Order {
  items: Array<{ product: string; quantity: number }>;
}

@Component({
  template: `
    @for (item of orderForm.items; track $index; let i = $index) {
      <div>
        <input [formField]="item.product" placeholder="Product" />
        <input [formField]="item.quantity" type="number" />
        <button type="button" (click)="removeItem(i)">Remove</button>
      </div>
    }
    <button type="button" (click)="addItem()">Add Item</button>
  `,
})
export class Order {
  orderModel = signal<Order>({
    items: [{ product: '', quantity: 1 }],
  });
  
  orderForm = form(this.orderModel, (schemaPath) => {
    applyEach(schemaPath.items, (item) => {
      required(item.product, { message: 'Product required' });
      min(item.quantity, 1, { message: 'Min quantity is 1' });
    });
  });
  
  addItem() {
    this.orderModel.update(m => ({
      ...m,
      items: [...m.items, { product: '', quantity: 1 }],
    }));
  }
  
  removeItem(index: number) {
    this.orderModel.update(m => ({
      ...m,
      items: m.items.filter((_, i) => i !== index),
    }));
  }
}
```


Back to the index: [angular-forms](angular-forms.md)
