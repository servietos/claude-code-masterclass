# Typed Reactive Forms

## Typed Reactive Forms

### Typed FormControl

```typescript
import { FormControl } from '@angular/forms';

// Inferred type: FormControl<string | null>
const name = new FormControl('');

// Non-nullable (no reset to null)
const email = new FormControl('', { nonNullable: true });
// Type: FormControl<string>

// With validators
const username = new FormControl('', {
  nonNullable: true,
  validators: [Validators.required, Validators.minLength(3)],
});
```

### Typed FormGroup

```typescript
import { FormGroup, FormControl } from '@angular/forms';

interface UserForm {
  name: FormControl<string>;
  email: FormControl<string>;
  age: FormControl<number | null>;
}

const form = new FormGroup<UserForm>({
  name: new FormControl('', { nonNullable: true }),
  email: new FormControl('', { nonNullable: true }),
  age: new FormControl<number | null>(null),
});

// Typed value access
const name: string = form.controls.name.value;
```

### NonNullableFormBuilder

```typescript
import { inject } from '@angular/core';
import { NonNullableFormBuilder } from '@angular/forms';

@Component({...})
export class Profile {
  private fb = inject(NonNullableFormBuilder);
  
  form = this.fb.group({
    name: ['', Validators.required],           // FormControl<string>
    email: ['', [Validators.required, Validators.email]],
    preferences: this.fb.group({
      newsletter: [false],                      // FormControl<boolean>
      theme: ['light' as 'light' | 'dark'],    // FormControl<'light' | 'dark'>
    }),
  });
}
```

Back to the index: [angular-form-patterns](angular-form-patterns.md)
