# Copying the shared frame into a target app

### The copied frame carries the reference app's environment contract

If the reference `app.component.ts` imports `../environments/environment.development`, every target needs
that file, with the same value for any key the frame reads. Two failure shapes:

- Target has both files but different values, so a spec asserting `environment.title` fails after the copy.
- Target uses the inverted convention (`environment.ts` for dev plus `environment.prod.ts` swapped in by
  `fileReplacements`), so the import does not resolve at all.

Reconcile the environment convention before the frame copy, and let a `environment.title` spec be the detector.

### `rm -rf` before `cp -r` deletes what only the target had

Replacing a shared directory wholesale drops any file unique to that copy (a spec, a local variant).
Run `diff -rq <ref> <target>` first and read the `Only in <target>` lines. Recover with
`git show HEAD:<path> > <path>`, never `git checkout --`. Read `git status` for ` D ` lines after any bulk
directory operation.

Back to the index: [material-tailwind-migration](material-tailwind-migration.md)
