# Support declared in prose: README matrices no tool can see

## 3. Libraries that declare framework support in prose, which no tool can see

### 3. Libraries that declare framework support in prose, which no tool can see

`npm outdated` and peer ranges both missed that the dashboard was running `@azure/msal-angular` v4 on Angular 22, an unsupported pairing. The truth lived in the package README:

```bash
sed -n '/## Version Support/,/## Prerequisites/p' node_modules/@azure/msal-angular/README.md
```

The real table has **three** columns and spells the version out in the first cell, which matters if you
parse it rather than read it:

```text
| MSAL Angular version | MSAL support status | Supported Angular versions |
| -------------------- | ------------------- | -------------------------- |
| MSAL Angular v6      | Active development  | 22                         |
| MSAL Angular v5      | In maintenance      | 19, 20, 21                 |
| MSAL Angular v4      | In maintenance      | 15, 16, 17, 18, 19, 20     |
```

**Rule: for any auth or platform SDK, read the README support matrix and the migration guide, not just the peer range.** A library can install cleanly, typecheck, build and pass tests while being formally unsupported on your framework version. Applies to MSAL, and to anything else that publishes a support table.

Back to the index: [angular-update](angular-update.md)
