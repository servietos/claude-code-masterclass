# Custom Form Validators

## Custom Validators

### Sync Validator

```typescript
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function forbiddenValue(forbidden: string): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    return control.value === forbidden 
      ? { forbiddenValue: { value: control.value } } 
      : null;
  };
}

// Usage
name: ['', [Validators.required, forbiddenValue('admin')]],
```

### Cross-Field Validator

```typescript
export function passwordMatch(): ValidatorFn {
  return (group: AbstractControl): ValidationErrors | null => {
    const password = group.get('password')?.value;
    const confirm = group.get('confirmPassword')?.value;
    return password === confirm ? null : { passwordMismatch: true };
  };
}

// Usage
form = this.fb.group({
  password: ['', [Validators.required, Validators.minLength(8)]],
  confirmPassword: ['', Validators.required],
}, { validators: passwordMatch() });
```

### Async Validator

```typescript
import { AsyncValidatorFn } from '@angular/forms';
import { map, catchError, of } from 'rxjs';

export function uniqueEmail(userService: User): AsyncValidatorFn {
  return (control: AbstractControl) => {
    return userService.checkEmail(control.value).pipe(
      map(exists => exists ? { emailTaken: true } : null),
      catchError(() => of(null))
    );
  };
}

// Usage
email: ['', 
  [Validators.required, Validators.email],  // sync validators
  [uniqueEmail(this.userService)]            // async validators
],
```

Back to the index: [angular-form-patterns](angular-form-patterns.md)
