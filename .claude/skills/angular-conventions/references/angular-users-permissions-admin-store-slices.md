# withAuth / withAdmin store slices and the API surface they wrap

## Shape

- **Two store slices** (`@ngrx/signals` `signalStoreFeature`, composed into the app store):
  - `withAuth()` — current user + permission checks. State `{ user, authEnabled, authType:'entra'|'local'|null,
    authResolved }`; seeds a `DEV_SUPERUSER` (`permissions:['*']`) when `!authEnabled`. Computeds:
    `isAuthenticated`, `hasPermission` (a computed **returning a function** → call `store.hasPermission()('x')`),
    `isAdmin`. Methods `setUser(user, authType)`, `clearUser()`, `markAuthResolved()`.
  - `withAdmin()` — data access (`rxMethod` + `tapResponse`): `loadUsers`, `saveUser`, `saveUserCredentials`,
    `setUserRoles`, `deleteUser`, `loadRoles`, `createRole`/`updateRole`/`deleteRole`, `loadPermissions`,
    `savePermissions({roleId,entries})`, `loadAdminEmails`.

## API surface wrapped

`GET/POST/PUT/DELETE /users` (+ `/{id}/roles`, `/{id}/credentials`), `GET/POST/PUT/DELETE /roles`,
`GET /permissions` + `PUT /permissions/{roleId}` (replace-all, persist only `canRead||canEdit`),
`GET /auth/{me,admins}`, `POST /auth/login`. See `add-mixed-auth` for the server contracts.

## Store slices (composed into `AppStore`, `store/app.store.ts`)

**`withAuth()`** — current user + permission checks. State `{ user: UserDto|null, authEnabled, authType:
'entra'|'local'|null, authResolved }`; seeds `DEV_SUPERUSER` (`permissions: ['*']`) when
`!environment.authEnabled`. Computeds: `isAuthenticated` (`!authEnabled || user!==null`),
`currentUserName`, **`userPermissions`**, `hasPermission`, `isAdmin`. Methods `setUser(user, authType)`,
`clearUser()`, `markAuthResolved()`.

**`withAdmin()`** — data access for the screens (all `rxMethod` + `tapResponse`, base
`environment.webApiUrl`): `loadUsers({text?,roleId?})`, `saveUser`, `saveUserCredentials`, `setUserRoles`,
`deleteUser`, `loadRoles`, `createRole`, `updateRole`, `deleteRole`, `loadPermissions`,
`savePermissions({roleId,entries})`, `loadAdminEmails`. State `{ users, usersTotalCount, roles,
permissions, adminEmails, *Loading }`.

API surface wrapped: `GET/POST/PUT/DELETE /api/users` (+ `/{id}/roles`, `/{id}/credentials`),
`GET/POST/PUT/DELETE /api/roles`, `GET /api/permissions` + `PUT /api/permissions/{roleId}` (replace-all,
only rows where `canRead||canEdit`), `GET /api/auth/{me,admins}`, `POST /api/auth/login`.

Back to the index: [angular-users-permissions-admin](angular-users-permissions-admin.md)
