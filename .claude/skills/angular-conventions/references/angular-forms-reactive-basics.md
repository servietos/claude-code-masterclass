# Reactive Forms Setup and Typing

## Reactive Forms (Production-Stable)

For production applications requiring stability guarantees, use Reactive Forms:

```typescript
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <input formControlName="email" />
      @if (form.controls.email.errors?.['required'] && form.controls.email.touched) {
        <span class="error">Email is required</span>
      }
      
      <input type="password" formControlName="password" />
      
      <button type="submit" [disabled]="form.invalid">Login</button>
    </form>
  `,
})
export class Login {
  private fb = inject(FormBuilder);
  
  form = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });
  
  onSubmit() {
    if (this.form.valid) {
      console.log(this.form.value);
    }
  }
}
```

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


Back to the index: [angular-forms](angular-forms.md)
