# Angular Signals: the signal store pattern

## Signal Store Pattern

For complex state, create a dedicated store:

```typescript
interface ProductState {
  products: Product[];
  selectedId: string | null;
  filter: string;
  loading: boolean;
  error: string | null;
}

@Injectable({ providedIn: 'root' })
export class ProductSt {
  // Private state
  private state = signal<ProductState>({
    products: [],
    selectedId: null,
    filter: '',
    loading: false,
    error: null,
  });
  
  // Selectors (computed signals)
  readonly products = computed(() => this.state().products);
  readonly selectedId = computed(() => this.state().selectedId);
  readonly filter = computed(() => this.state().filter);
  readonly loading = computed(() => this.state().loading);
  readonly error = computed(() => this.state().error);
  
  readonly filteredProducts = computed(() => {
    const { products, filter } = this.state();
    if (!filter) return products;
    return products.filter(p => 
      p.name.toLowerCase().includes(filter.toLowerCase())
    );
  });
  
  readonly selectedProduct = computed(() => {
    const { products, selectedId } = this.state();
    return products.find(p => p.id === selectedId) ?? null;
  });
  
  private http = inject(HttpClient);
  
  // Actions
  setFilter(filter: string): void {
    this.state.update(s => ({ ...s, filter }));
  }
  
  selectProduct(id: string | null): void {
    this.state.update(s => ({ ...s, selectedId: id }));
  }
  
  async loadProducts(): Promise<void> {
    this.state.update(s => ({ ...s, loading: true, error: null }));
    
    try {
      const products = await firstValueFrom(
        this.http.get<Product[]>('/api/products')
      );
      this.state.update(s => ({ ...s, products, loading: false }));
    } catch (err) {
      this.state.update(s => ({ 
        ...s, 
        loading: false, 
        error: 'Failed to load products' 
      }));
    }
  }
  
  async addProduct(product: Omit<Product, 'id'>): Promise<void> {
    const newProduct = await firstValueFrom(
      this.http.post<Product>('/api/products', product)
    );
    this.state.update(s => ({
      ...s,
      products: [...s.products, newProduct],
    }));
  }
}
```

Back to the index: [angular-signals-patterns](angular-signals-patterns.md)
