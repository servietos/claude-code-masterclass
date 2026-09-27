# Signal Forms Gotchas

## Gotchas

### No HTML validation attributes on `[formField]`

Do not put `required`, `maxlength`, `minlength`, or any other HTML validation attribute on an element that has `[formField]`. Angular raises NG8022 at compile time.

```typescript
// WRONG — causes NG8022
// <input [formField]="form.name" required maxlength="100" />

// CORRECT — use schema validators
const myForm = form(this.model, (s) => {
  required(s.name, { message: 'Name is required' });
  maxLength(s.name, 100, { message: 'Max 100 characters' });
});
```

### Integer ID fields must be `string` in the form model

`[formField]` on a `<select>` expects the bound field to be typed as `string`. If an ID field (e.g. `typeId`, `contractId`, `memberId`) is typed as `number | null` in the form model, the select binding will not round-trip correctly. Declare the field as `string` in the form interface and cast back to a number when emitting.

```typescript
interface ContractFormData {
  typeId: string;
  memberId: string;
  amount: number | null;
}

const model = signal<ContractFormData>({ typeId: '', memberId: '', amount: null });
const contractForm = form(model);
```

```html
<select [formField]="contractForm.typeId">
  @for (t of types(); track t.id) {
    <option [value]="t.id">{{ t.name }}</option>
  }
</select>
```

```typescript
onSave() {
  const f = this.model();
  const payload = {
    typeId: f.typeId ? +f.typeId : null,
    memberId: f.memberId ? +f.memberId : null,
    amount: f.amount,
  };
}
```

### Native time inputs — enforcing minute steps

`<input type="time" step="300">` (300s = 5 min) restricts spinner increments and constraint
validation to 5-minute marks, but does **not** restrict Chrome's dropdown/list time picker —
that list still offers every minute (00, 01, 02 …). `step` alone cannot force 5-minute-only
selection.

Pair `step` with a snap-to-nearest-step correction on `(change)`, so a picker click or pasted
value gets rounded after the fact. Reuse an existing helper rather than reimplementing it — e.g.
a `roundTimeStringToStep(time, stepMinutes)` util under the app's shared utils
(`<app>/shared/utils/time-functions.ts`, unit-tested in `time-functions.spec.ts`). Wire it into
the start/end time fields of the component's `.ts` and `.html` like this:

```typescript
snapTimeToStep(controlName: 'StartTime' | 'EndTime', event: Event): void {
  const value = (event.target as HTMLInputElement).value;
  const rounded = roundTimeStringToStep(value, 5);
  // patch rounded value back into the form model
}
```

```html
<input type="time" step="300" [formField]="form.StartTime" (change)="snapTimeToStep('StartTime', $event)" />
```

Whenever a native time field must be constrained to N-minute intervals, use **both**
`step` (spinner/validity + a11y) **and** the snap-on-change correction (gates the picker
list and any typed/pasted value).


Back to the index: [angular-forms](angular-forms.md)
