# Hierarchical Injection

## Hierarchical Injection

### Component Tree Injection

```typescript
// Parent provides service
@Component({
  selector: 'app-form-container',
  providers: [FormState],
  template: `
    <app-form-header />
    <app-form-body />
    <app-form-footer />
  `,
})
export class FormContainer {
  private formState = inject(FormState);
}

// Children share same instance
@Component({
  selector: 'app-form-body',
  template: `...`,
})
export class FormBody {
  // Gets same instance as parent
  private formState = inject(FormState);
}

// Grandchildren also share
@Component({
  selector: 'app-form-field',
  template: `...`,
})
export class FormField {
  // Gets same instance from ancestor
  private formState = inject(FormState);
}
```

### viewProviders vs providers

```typescript
@Component({
  selector: 'app-tabs',
  // providers: Available to component AND content children
  providers: [TabsSvc],

  // viewProviders: Available to component AND view children only
  // NOT available to content children (<ng-content>)
  viewProviders: [InternalTabs],
  
  template: `
    <div class="tabs">
      <ng-content /> <!-- Content children can't access viewProviders -->
    </div>
  `,
})
export class Tabs {}
```

Back to the index: [angular-di-patterns](angular-di-patterns.md)
