# Defer Blocks and Lazy Loading

## Dynamic Components

Using `@defer` for lazy loading:

```typescript
@Component({
  template: `
    @defer (on viewport) {
      <app-heavy-chart [data]="chartData()" />
    } @placeholder {
      <div class="chart-placeholder">Loading chart...</div>
    } @loading (minimum 500ms) {
      <app-spinner />
    } @error {
      <p>Failed to load chart</p>
    }
  `,
})
export class Dashboard {
  chartData = input.required<ChartData>();
}
```

Defer triggers:
- `on viewport` - When element enters viewport
- `on idle` - When browser is idle
- `on interaction` - On user interaction (click, focus)
- `on hover` - On mouse hover
- `on immediate` - Immediately after non-deferred content
- `on timer(500ms)` - After specified delay
- `when condition` - When expression becomes true

```typescript
@Component({
  template: `
    @defer (on interaction; prefetch on idle) {
      <app-comments [postId]="postId()" />
    } @placeholder {
      <button>Load Comments</button>
    }
  `,
})
export class Post {
  postId = input.required<string>();
}
```

Back to the index: [angular-component-patterns](angular-component-patterns.md)
