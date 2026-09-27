# Attribute Directive and Error Boundary

## Attribute Directives on Components

```typescript
@Directive({
  selector: '[appHighlight]',
  host: {
    '[style.backgroundColor]': 'color()',
  },
})
export class Highlight {
  color = input('yellow', { alias: 'appHighlight' });
}

// Usage on component
@Component({
  imports: [Highlight],
  template: `<app-card appHighlight="lightblue" />`,
})
export class Page {}
```

## Error Boundaries

```typescript
@Component({
  selector: 'app-error-boundary',
  template: `
    @if (hasError()) {
      <div class="error">
        <h3>Something went wrong</h3>
        <button (click)="retry()">Retry</button>
      </div>
    } @else {
      <ng-content />
    }
  `,
})
export class ErrorBoundary {
  hasError = signal(false);
  private errorHandler = inject(ErrorHandler);
  
  retry() {
    this.hasError.set(false);
  }
}
```

Back to the index: [angular-component-patterns](angular-component-patterns.md)
