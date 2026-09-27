# Breadcrumbs from Route Data

## Breadcrumbs

```typescript
// breadcrumb.service.ts
@Injectable({ providedIn: 'root' })
export class Breadcrumb {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  breadcrumbs = toSignal(
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(() => this.buildBreadcrumbs(this.route.root))
    ),
    { initialValue: [] }
  );
  
  private buildBreadcrumbs(
    route: ActivatedRoute,
    url: string = '',
    breadcrumbs: Breadcrumb[] = []
  ): Breadcrumb[] {
    const children = route.children;
    
    if (children.length === 0) {
      return breadcrumbs;
    }
    
    for (const child of children) {
      const routeUrl = child.snapshot.url
        .map(segment => segment.path)
        .join('/');
      
      if (routeUrl) {
        url += `/${routeUrl}`;
      }
      
      const label = child.snapshot.data['breadcrumb'];
      if (label) {
        breadcrumbs.push({ label, url });
      }
      
      return this.buildBreadcrumbs(child, url, breadcrumbs);
    }
    
    return breadcrumbs;
  }
}

// Route config with breadcrumb data
export const routes: Routes = [
  {
    path: 'products',
    data: { breadcrumb: 'Products' },
    children: [
      { path: '', component: ProductList },
      {
        path: ':id',
        data: { breadcrumb: 'Product Details' },
        component: ProductDetail,
      },
    ],
  },
];

// breadcrumb.component.ts
@Component({
  selector: 'app-breadcrumb',
  template: `
    <nav aria-label="Breadcrumb">
      <ol>
        <li><a routerLink="/">Home</a></li>
        @for (crumb of breadcrumbService.breadcrumbs(); track crumb.url) {
          <li>
            <a [routerLink]="crumb.url">{{ crumb.label }}</a>
          </li>
        }
      </ol>
    </nav>
  `,
})
export class BreadcrumbCmpt {
  breadcrumbService = inject(Breadcrumb);
}
```

Back to the index: [angular-routing](angular-routing.md)
