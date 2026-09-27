# MSAL Angular support matrix: pick the right major

## Pick the right major first

`npm outdated` cannot see this and neither can the peer range: msal-angular publishes its supported Angular versions as a table in its README. Read it from the installed package before deciding anything:

```bash
sed -n '/## Version Support/,/## Prerequisites/p' node_modules/@azure/msal-angular/README.md
```

| MSAL Angular version | Supported Angular versions |
| --- | --- |
| v6 (active development) | 22 |
| v5 (maintenance) | 19, 20, 21 |
| v4 (maintenance) | 15, 16, 17, 18, 19, 20 |

**On Angular 22, only msal-angular v6 is supported**, and v6 requires `@azure/msal-browser ^5.18.0`, so the two move together. A v4 app on Angular 22 installs, typechecks, builds and passes its tests while being formally unsupported; that exact combination was found in `dashboard.integrations.at` on 2026-08-10 with nothing flagging it. Verify the pairing with `npm ls @azure/msal-angular @azure/msal-browser` plus the table above, not with `npm outdated`.

Back to the index: [msal-version-changes](msal-version-changes.md)
