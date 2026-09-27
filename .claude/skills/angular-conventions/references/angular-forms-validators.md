# Signal Forms Validators

## Validation

### Built-in Validators

```typescript
import { 
  form, required, email, min, max, 
  minLength, maxLength, pattern 
} from '@angular/forms/signals';

const userForm = form(this.userModel, (schemaPath) => {
  // Required field
  required(schemaPath.name, { message: 'Name is required' });
  
  // Email format
  email(schemaPath.email, { message: 'Invalid email' });
  
  // Numeric range
  min(schemaPath.age, 18, { message: 'Must be 18+' });
  max(schemaPath.age, 120, { message: 'Invalid age' });
  
  // String/array length
  minLength(schemaPath.password, 8, { message: 'Min 8 characters' });
  maxLength(schemaPath.bio, 500, { message: 'Max 500 characters' });
  
  // Regex pattern
  pattern(schemaPath.phone, /^\d{3}-\d{3}-\d{4}$/, {
    message: 'Format: 555-123-4567',
  });
});
```

### Custom Validators

```typescript
import { validate } from '@angular/forms/signals';

const signupForm = form(this.signupModel, (schemaPath) => {
  // Custom validation logic
  validate(schemaPath.username, ({ value }) => {
    if (value().includes(' ')) {
      return { kind: 'noSpaces', message: 'Username cannot contain spaces' };
    }
    return null;
  });
});
```

### Cross-Field Validation

```typescript
const passwordForm = form(this.passwordModel, (schemaPath) => {
  required(schemaPath.password);
  required(schemaPath.confirmPassword);
  
  // Compare fields
  validate(schemaPath.confirmPassword, ({ value, valueOf }) => {
    if (value() !== valueOf(schemaPath.password)) {
      return { kind: 'mismatch', message: 'Passwords do not match' };
    }
    return null;
  });
});
```

### Async Validation

```typescript
import { validateHttp } from '@angular/forms/signals';

const signupForm = form(this.signupModel, (schemaPath) => {
  validateHttp(schemaPath.username, {
    request: ({ value }) => `/api/check-username?u=${value()}`,
    onSuccess: (response: { taken: boolean }) => {
      if (response.taken) {
        return { kind: 'taken', message: 'Username already taken' };
      }
      return null;
    },
    onError: () => ({
      kind: 'networkError',
      message: 'Could not verify username',
    }),
  });
});
```


Back to the index: [angular-forms](angular-forms.md)
