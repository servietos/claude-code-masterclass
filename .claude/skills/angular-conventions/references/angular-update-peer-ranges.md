# Reading peer ranges: TypeScript and third-party @angular/core peers

## 1. TypeScript: read the peer range off the compiler, never take latest

### 1. TypeScript: read the peer range off the compiler, never take latest

Angular pins a narrow TypeScript window. Read it from the installed compiler:

```bash
node -e "const p=require('./node_modules/@angular/compiler-cli/package.json'); console.log(p.version, JSON.stringify(p.peerDependencies))"
```

On Angular 22.1.1 this prints `22.1.1 {"@angular/compiler":"22.1.1","typescript":">=6.0 <6.1"}`. TypeScript 7.0.2 was available and is **out of range**, so it stays unbumped. The `>=x <y` form is the authority; a green build on an out-of-range TS proves nothing, because the compiler only warns on some mismatches.

## 2. Third-party libraries with an `@angular/core` peer lag the framework

### 2. Third-party libraries with an `@angular/core` peer lag the framework

Check the tag before assuming a compatible release exists:

```bash
npm view <pkg> dist-tags --json
npm view <pkg>@<version> peerDependencies --json
```

`@ngrx/signals` was `{"latest":"21.1.1","next":"22.0.0-rc.0"}`, with 21.1.1 peering `@angular/core: ^21.0.0`. So on Angular 22 the choice is stable-with-unmet-peer versus a release candidate.

**Rule: prefer the stable version with an unmet peer over an RC**, unless the RC fixes a bug you are actually hitting. An unmet peer is a warning the install already absorbs; an RC is unreleased code in a production dependency. Re-check when the stable major ships.

Check each package separately rather than assuming a family moves together: `@ngrx/operators@21.1.1` declares **no** `@angular/core` peer at all (`{"rxjs":"^6.5.3 || ^7.4.0"}`), so only `@ngrx/signals` was ever unmet. Reporting both as blocked would have been wrong.

Back to the index: [angular-update](angular-update.md)
