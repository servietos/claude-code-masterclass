# Testing with DI

## Testing with DI

### Mocking Services

```typescript
describe('UserCmpt', () => {
  let userServiceSpy: jasmine.SpyObj<User>;
  
  beforeEach(async () => {
    userServiceSpy = jasmine.createSpyObj('User', ['getUser', 'updateUser']);
    userServiceSpy.getUser.and.returnValue(of({ id: '1', name: 'Test' }));
    
    await TestBed.configureTestingModule({
      imports: [UserCmpt],
      providers: [
        { provide: User, useValue: userServiceSpy },
      ],
    }).compileComponents();
  });
  
  it('should load user', () => {
    const fixture = TestBed.createComponent(UserCmpt);
    fixture.detectChanges();
    
    expect(userServiceSpy.getUser).toHaveBeenCalled();
  });
});
```

### Overriding Providers

```typescript
describe('with different config', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
    })
    .overrideProvider(APP_CONFIG, {
      useValue: { apiUrl: 'http://test-api.com' },
    })
    .compileComponents();
  });
});
```

### Testing Injection Tokens

```typescript
describe('API_URL token', () => {
  it('should provide correct URL', () => {
    TestBed.configureTestingModule({
      providers: [
        { provide: API_URL, useValue: 'https://api.test.com' },
      ],
    });
    
    const apiUrl = TestBed.inject(API_URL);
    expect(apiUrl).toBe('https://api.test.com');
  });
});
```

Back to the index: [angular-di-patterns](angular-di-patterns.md)
