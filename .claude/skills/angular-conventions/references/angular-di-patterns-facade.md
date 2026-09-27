# Facade Service

## Service Patterns

### Facade Service

Combine multiple services into a single API:

```typescript
@Injectable({ providedIn: 'root' })
export class ShopFacade {
  private productService = inject(Product);
  private cartService = inject(Cart);
  private orderService = inject(Order);
  
  // Expose combined state
  readonly products = this.productService.products;
  readonly cart = this.cartService.items;
  readonly cartTotal = this.cartService.total;
  
  // Unified actions
  addToCart(productId: string, quantity: number) {
    const product = this.productService.getById(productId);
    if (product) {
      this.cartService.add(product, quantity);
    }
  }
  
  async checkout() {
    const items = this.cartService.items();
    const order = await this.orderService.create(items);
    this.cartService.clear();
    return order;
  }
}
```

Back to the index: [angular-di-patterns](angular-di-patterns.md)
