# Angular Signals: testing and debugging

## Testing Signals

```typescript
describe('Counter', () => {
  it('should increment count', () => {
    const component = new Counter();
    
    expect(component.count()).toBe(0);
    
    component.increment();
    expect(component.count()).toBe(1);
    
    component.increment();
    expect(component.count()).toBe(2);
  });
  
  it('should compute doubled value', () => {
    const component = new Counter();
    
    expect(component.doubled()).toBe(0);
    
    component.count.set(5);
    expect(component.doubled()).toBe(10);
  });
});

describe('ProductSt', () => {
  let store: ProductSt;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ProductSt,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    store = TestBed.inject(ProductSt);
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should filter products', () => {
    // Set initial state
    store['state'].set({
      products: [
        { id: '1', name: 'Apple' },
        { id: '2', name: 'Banana' },
      ],
      selectedId: null,
      filter: '',
      loading: false,
      error: null,
    });
    
    expect(store.filteredProducts().length).toBe(2);
    
    store.setFilter('app');
    expect(store.filteredProducts().length).toBe(1);
    expect(store.filteredProducts()[0].name).toBe('Apple');
  });
});
```

## Signal Debugging

```typescript
// Debug effect to log signal changes
effect(() => {
  console.log('State changed:', {
    count: this.count(),
    items: this.items(),
    filter: this.filter(),
  });
});

// Conditional debugging
const DEBUG = signal(false);

effect(() => {
  if (untracked(() => DEBUG())) {
    console.log('Debug:', this.state());
  }
});
```

Back to the index: [angular-signals-patterns](angular-signals-patterns.md)
