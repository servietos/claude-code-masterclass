# Conditional Validation and Fields

### Conditional Validation

```typescript
const orderForm = form(this.orderModel, (schemaPath) => {
  required(schemaPath.promoCode, {
    message: 'Promo code required for discounts',
    when: ({ valueOf }) => valueOf(schemaPath.applyDiscount),
  });
});
```

**Toggle gates a sibling field.** A boolean toggle (`enabled`) that both makes a sibling field
`required` and `disabled` when off — the pattern used e.g. in an admin test-panel:

```typescript
testModel = signal({ enabled: false, receiver: '' });
testForm = form(this.testModel, (p) => {
  required(p.receiver, { message: 'Email address is required', when: ({ valueOf }) => valueOf(p.enabled) });
  email(p.receiver, { when: ({ valueOf }) => valueOf(p.enabled) });
  disabled(p.receiver, ({ valueOf }) => !valueOf(p.enabled));
});
```

```html
<input type="email" [formField]="testForm.receiver" />
@if (testForm.receiver().touched() && testForm.receiver().invalid()) {
  <span class="error">{{ testForm.receiver().errors()[0].message }}</span>
}
```

Gate validation display on `touched()` so no error shows before interaction, and gate `required`
on the controlling toggle so the field isn't required while the feature is off.

## Conditional Fields

### Hidden Fields

```typescript
import { hidden } from '@angular/forms/signals';

const profileForm = form(this.profileModel, (schemaPath) => {
  hidden(schemaPath.publicUrl, ({ valueOf }) => !valueOf(schemaPath.isPublic));
});
```

```html
@if (!profileForm.publicUrl().hidden()) {
  <input [formField]="profileForm.publicUrl" />
}
```

### Disabled Fields

```typescript
import { disabled } from '@angular/forms/signals';

const orderForm = form(this.orderModel, (schemaPath) => {
  disabled(schemaPath.couponCode, ({ valueOf }) => valueOf(schemaPath.total) < 50);
});
```

### Readonly Fields

```typescript
import { readonly } from '@angular/forms/signals';

const accountForm = form(this.accountModel, (schemaPath) => {
  readonly(schemaPath.username); // Always readonly
});
```


Back to the index: [angular-forms](angular-forms.md)
