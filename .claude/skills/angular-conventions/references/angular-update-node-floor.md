# The Node floor: where it is pinned and what the base image bundles

## 7. The Node floor moves inside a minor line, and it does not live in CI

### 7. The Node floor moves inside a minor line, and it does not live in CI

Angular's `engines.node` is not stable across a major. Angular 22.1.x declares:

```bash
npm view @angular/cli@22.1.4 engines --json
# {"node":"^22.22.3 || ^24.15.0 || >=26.0.0", "npm":"^6.11.0 || ^7.5.6 || >=8.0.0"}
```

A 22.0.x to 22.1.x bump raised that floor **within the same major**. So "we are already on the right
Node major" is not a compatibility answer: read the range off the exact CLI version you land on, every
time, and reconcile it against whatever pins Node in the build.

**Where Node is pinned is the part that gets looked for in the wrong place.** Asked to upgrade the Node
version "in the workflows", a grep of all 20 workflow files for `setup-node|node-version|NODE_VERSION`
returned zero hits, because every app is built inside its image by `docker/build-push-action@v6` and CI
never installs Node at all. The version was four `FROM node:22` lines in four Dockerfiles. An empty grep
here is the answer, not a failed search: **find where Node enters the build before changing anything**,
and do not add a `setup-node` step to a workflow that builds in Docker, because it is dead configuration
that will later read as the authoritative pin.

A **floating** base tag is not a pin. `FROM node:22` resolved to 22.23.2 that day, which satisfied
`^22.22.3`, so the images built: by luck, since the tag floats and the floor had just moved up inside the
line it floats over. Pin an explicit version that satisfies the range (`FROM node:24.19.0`, keeping each
file's existing `-alpine` or Debian flavour, because `npm rebuild lightningcss` and `--include=optional`
behave differently between them).

**And re-read what the new base image bundles.** Three of the four Dockerfiles carried
`RUN npm install -g npm@11.12.1`. On `node:22` that was an upgrade; on `node:24.19.0`, which bundles npm
11.17.0 (`docker run --rm node:24.19.0 npm -v`), the identical line is now a **downgrade**. That may
still be what you want, since the lockfiles were regenerated with that npm, but it is no longer doing
what its author meant, so decide it deliberately rather than leaving it to read as a no-op.

Verify by building the image, not by building on the host: `npm ci` inside a fresh image is the only
thing that proves the pinned base installs the bumped tree. A green host `ng build` says nothing about
the image's Node.

Back to the index: [angular-update](angular-update.md)
