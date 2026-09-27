# Manifest floors and the repo install convention

## 5. Caret floors are the deployed version when the image has no lockfile

### 5. Caret floors are the deployed version when the image has no lockfile

Check how the image installs before assuming the lockfile governs:

```bash
grep -nE "COPY package|npm (ci|install)" Dockerfile
```

The dashboard `Dockerfile` copies **only** `package.json` and runs `npm install`, no lockfile. A floor of `^22.0.0` therefore ships whatever npm resolves at image build time, not the version the green lockfile pinned; and a floor of `^4.0.15` would have rebuilt the image on MSAL v4 no matter what the lockfile said.

**Rule: after any update, raise the manifest floor to the version you actually tested.** `ng update` does this for the packages it touches; anything you bump by hand needs it done deliberately. It is what makes the manifest a record of a tested combination rather than a wish.

## 6. Repo install convention

### 6. Repo install convention

Both Dockerfiles install with `--legacy-peer-deps`, so local commands must match or they fail on `ERESOLVE` where the image succeeds:

```bash
npm update --legacy-peer-deps
npm install --save-dev --legacy-peer-deps <pkg>@<version>
```

Back to the index: [angular-update](angular-update.md)
