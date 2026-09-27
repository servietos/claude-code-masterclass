# Login, Auth Guard and returnUrl

## Authentication Flow

### Complete Auth Setup

```typescript
// auth.service.ts
@Injectable({ providedIn: 'root' })
export class Auth {
  private _user = signal<User | null>(null);
  private _token = signal<string | null>(null);
  
  readonly user = this._user.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null);
  
  private router = inject(Router);
  private http = inject(HttpClient);
  
  async login(credentials: Credentials): Promise<boolean> {
    try {
      const response = await firstValueFrom(
        this.http.post<AuthResponse>('/api/login', credentials)
      );
      
      this._token.set(response.token);
      this._user.set(response.user);
      localStorage.setItem('token', response.token);
      
      return true;
    } catch {
      return false;
    }
  }
  
  logout(): void {
    this._user.set(null);
    this._token.set(null);
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }
  
  async checkAuth(): Promise<boolean> {
    const token = localStorage.getItem('token');
    if (!token) return false;
    
    try {
      const user = await firstValueFrom(
        this.http.get<User>('/api/me')
      );
      this._user.set(user);
      this._token.set(token);
      return true;
    } catch {
      localStorage.removeItem('token');
      return false;
    }
  }
}

// auth.guard.ts
export const authGuard: CanActivateFn = async (route, state) => {
  const authService = inject(Auth);
  const router = inject(Router);
  
  // Check if already authenticated
  if (authService.isAuthenticated()) {
    return true;
  }
  
  // Try to restore session
  const isValid = await authService.checkAuth();
  if (isValid) {
    return true;
  }
  
  // Redirect to login
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};

// login.component.ts
@Component({
  template: `
    <form (ngSubmit)="login()">
      <input [(ngModel)]="email" name="email" />
      <input [(ngModel)]="password" name="password" type="password" />
      <button type="submit">Login</button>
    </form>
  `,
})
export class Login {
  private authService = inject(Auth);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  email = '';
  password = '';
  
  async login() {
    const success = await this.authService.login({
      email: this.email,
      password: this.password,
    });
    
    if (success) {
      const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
      this.router.navigateByUrl(returnUrl);
    }
  }
}
```

Back to the index: [angular-routing-patterns](angular-routing-patterns.md)
