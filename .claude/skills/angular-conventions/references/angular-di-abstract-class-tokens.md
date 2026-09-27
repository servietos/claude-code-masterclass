# Abstract Classes as Tokens

## Abstract Classes as Tokens

Use abstract classes for better type safety:

```typescript
// Abstract service definition
export abstract class Logger {
  abstract log(message: string): void;
  abstract error(message: string, error?: Error): void;
  abstract warn(message: string): void;
}

// Console implementation
@Injectable()
export class ConsoleLog extends Logger {
  log(message: string) {
    console.log(`[LOG] ${message}`);
  }
  
  error(message: string, error?: Error) {
    console.error(`[ERROR] ${message}`, error);
  }
  
  warn(message: string) {
    console.warn(`[WARN] ${message}`);
  }
}

// Remote implementation
@Injectable()
export class RemoteLog extends Logger {
  private http = inject(HttpClient);
  
  log(message: string) {
    this.send('log', message);
  }
  
  error(message: string, error?: Error) {
    this.send('error', message, error);
  }
  
  warn(message: string) {
    this.send('warn', message);
  }
  
  private send(level: string, message: string, error?: Error) {
    this.http.post('/api/logs', { level, message, error: error?.message }).subscribe();
  }
}

// Provide based on environment
{
  provide: Logger,
  useClass: environment.production ? RemoteLog : ConsoleLog,
}

// Inject using abstract class
@Injectable({ providedIn: 'root' })
export class User {
  private logger = inject(Logger);

  createUser(user: UserData) {
    this.logger.log(`Creating user: ${user.email}`);
    // ...
  }
}
```

Back to the index: [angular-di](angular-di.md)
