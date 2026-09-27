# Running the v4 to v6 bump

## v4 to v6 upgrade: what actually changes

Going 4 to 6 crosses both the v4 to v5 and v5 to v6 guides. In practice the code delta is small; the audit is the work.

Bump both packages in one install, because v6 peers on msal-browser `^5.18.0` and a partial bump leaves an unresolvable tree:

```bash
npm install --legacy-peer-deps @azure/msal-angular@^6.0.3 @azure/msal-browser@^5.18.0
```

`npm install` writes the new caret floors into `package.json` itself. Confirm it did, because a Dockerfile that copies only `package.json` and runs `npm install` (no lockfile) would otherwise rebuild the image on v4 regardless of a green lockfile. See `angular-update.md`, "Caret floors are the deployed version".

### The one required code change: `navigateToLoginRequestUrl` moved

It did not disappear in v5, it **relocated** from the `PublicClientApplication` config into the `handleRedirectPromise()` / `handleRedirectObservable()` call:

```typescript
// v4: in BrowserAuthOptions (no longer valid)
new PublicClientApplication({ auth: { ..., navigateToLoginRequestUrl: false } });

// v5+: an option on the call
provideAppInitializer(() => {
  const msal = inject(MsalService);
  return firstValueFrom(
    msal.initialize().pipe(
      concatMap(() => msal.handleRedirectObservable({ navigateToLoginRequestUrl: false })),
    ),
    { defaultValue: null },
  );
});
```

Passing a bare hash string to `handleRedirectObservable()` is deprecated; use the options object.

## See Also

- [`angular-msal-auth.md`](angular-msal-auth.md) - the wiring the new APIs go into
- [`msal-angular.md`](msal-angular.md) - provider setup, `AuthStateService`, migration checklist
- [`msal-troubleshooting.md`](msal-troubleshooting.md) - symptoms an unfinished upgrade produces

Back to the index: [msal-version-changes](msal-version-changes.md)
