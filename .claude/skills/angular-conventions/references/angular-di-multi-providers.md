# Multi Providers

## Multi Providers

Collect multiple values for same token:

```typescript
// Token for multiple validators
export const VALIDATORS = new InjectionToken<Validator[]>('Validators');

// Provide multiple values
providers: [
  { provide: VALIDATORS, useClass: RequiredValidator, multi: true },
  { provide: VALIDATORS, useClass: EmailValidator, multi: true },
  { provide: VALIDATORS, useClass: MinLengthValidator, multi: true },
]

// Inject as array
@Injectable()
export class Validation {
  private validators = inject(VALIDATORS); // Validator[]
  
  validate(value: string): ValidationError[] {
    return this.validators
      .map(v => v.validate(value))
      .filter(Boolean);
  }
}
```

### HTTP Interceptors (Multi Provider)

```typescript
// Interceptors use multi providers internally
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        authInterceptor,
        loggingInterceptor,
        errorInterceptor,
      ])
    ),
  ],
};
```

Back to the index: [angular-di](angular-di.md)
