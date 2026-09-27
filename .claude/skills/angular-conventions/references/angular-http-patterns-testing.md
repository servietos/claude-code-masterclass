# Angular HTTP: Testing

## Testing HTTP

### Testing httpResource

```typescript
describe('UserCmpt', () => {
  let component: UserCmpt;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [UserCmpt],
      providers: [provideHttpClientTesting()],
    });
    
    component = TestBed.createComponent(UserCmpt).componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should load user', () => {
    component.userId.set('123');
    
    const req = httpMock.expectOne('/api/users/123');
    req.flush({ id: '123', name: 'Test User' });
    
    expect(component.userResource.value()?.name).toBe('Test User');
  });
  
  afterEach(() => {
    httpMock.verify();
  });
});
```

### Testing Services

```typescript
describe('User', () => {
  let service: User;
  let httpMock: HttpTestingController;
  
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        User,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    
    service = TestBed.inject(User);
    httpMock = TestBed.inject(HttpTestingController);
  });
  
  it('should create user', () => {
    const newUser = { name: 'Test', email: 'test@example.com' };
    
    service.create(newUser).subscribe(user => {
      expect(user.id).toBeDefined();
      expect(user.name).toBe('Test');
    });
    
    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(newUser);
    
    req.flush({ id: '1', ...newUser });
  });
});
```

Back to the index: [angular-http-patterns](angular-http-patterns.md)
