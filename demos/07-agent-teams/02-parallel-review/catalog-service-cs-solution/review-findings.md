# Review Findings

Three reviewers, one lens each: **security** (Controllers/, Common/AppConfig.cs, Common/AppBuilder.cs, appsettings.json, Program.cs), **performance** (Infrastructure/FoodDBContext.cs and the FoodController.cs query paths), **tests** (whole project, testability and coverage). 41 findings, every line verified against the file by the reviewer who filed it. No source file was changed.

Where two lenses filed the same line, they are separate rows because the reviewers established they are separate defects, not duplicates.

## Ranked findings

| #   | Severity | Lens        | File                             | Line  | Description                                                                                                                             |
| --- | -------- | ----------- | -------------------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | critical | security    | appsettings.json                 | 26    | Live Azure SQL admin credentials sit in plaintext against a named server in a file that is untracked but not gitignored, so the next `git add .` writes the secret into history permanently. |
| 2   | critical | security    | Controllers/ConfigController.cs  | 25    | `cfg.Get<AppConfig>()` binds the whole configuration root and line 26 serves it anonymously, leaking the SQL password and the App Insights ingestion key. |
| 3   | critical | security    | Controllers/ConfigController.cs  | 33    | `GetEnvVars()` returns the entire process environment to any anonymous caller, which on App Service means every app setting, connection string and platform secret. |
| 4   | critical | performance | Controllers/FoodController.cs    | 51    | `var item = GetById(id);` is never awaited, so the guard on line 52 is always true and line 54 hands a `Task` to `ctx.Remove`, leaving DELETE with no working path. |
| 5   | critical | tests       | Controllers/FoodController.cs    | 51    | Nothing asserts that DELETE removes a row, and the endpoint returns 200 regardless of what happened. |
| 6   | critical | tests       | Infrastructure/FoodDBContext.cs  | 17    | No schema, no seed and no database file reach a fresh clone, so no integration test can stand up a populated database. |
| 7   | critical | tests       | catalog-service.csproj           | 28    | `coverlet.msbuild` is referenced as a coverage collector while no test project, solution or test file exists anywhere under this folder. |
| 8   | high     | security    | Program.cs                       | 31    | Authentication and the global `AuthorizeFilter` register only when `cfg.App.AuthEnabled` is true, appsettings.json:21 sets it false, and no `[Authorize]` attribute exists anywhere, so every route is anonymous. |
| 9   | high     | performance | Infrastructure/FoodDBContext.cs  | 17    | The only `Database.EnsureCreated()` sits in a parameterless constructor that configures no provider and that `Program.cs` never calls, and there is no Migrations folder, so the `HasData` seed never reaches a database. |
| 10  | high     | security    | Controllers/FoodController.cs    | 41    | `Attach` plus `State = Modified` on a caller-supplied entity with no existence, ownership or ModelState check lets any anonymous caller overwrite any row by ID. |
| 11  | high     | tests       | Controllers/FoodController.cs    | 41    | The full-column write is demonstrated by the repo's own fixture at test-controllers.http:42-48, which omits `inStock` and `pictureUrl`, and no round-trip test catches the clobber. |
| 12  | high     | security    | Controllers/FoodController.cs    | 49    | `DeleteFood` is an anonymous destructive route with no authorization of any kind. |
| 13  | high     | performance | Controllers/FoodController.cs    | 18    | `await ctx.Food.ToArrayAsync()` materializes the entire Food table with no paging, filter or `Take`, so response size and server memory grow linearly with row count forever. |
| 14  | high     | security    | Common/AppBuilder.cs             | 131   | CORS combines `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` and is applied unconditionally in every environment, so any origin can drive the write endpoints. |
| 15  | high     | tests       | Program.cs                       | 12    | Top-level statements with no `public partial class Program` and no `InternalsVisibleTo` mean `WebApplicationFactory<Program>` cannot bind the entry point, which blocks the in-process test that would cover most findings on all three lists. |
| 16  | high     | tests       | Program.cs                       | 31    | No fixture overrides the `AuthEnabled` flag, so no test can assert that a 401 is ever reachable. |
| 17  | high     | tests       | Controllers/ConfigController.cs  | 26    | `Ok(config)` returns the bound `AppConfig` carrying the live password, and no test asserts the response body. |
| 18  | high     | tests       | Controllers/ConfigController.cs  | 34    | `Ok(val)` returns the full process environment, trivially assertable over HTTP and entirely unasserted. |
| 19  | high     | tests       | Infrastructure/FoodDBContext.cs  | 15    | The parameterless constructor builds options with no provider, so `new FoodDBContext()` throws before any assertion runs, and the csproj references no in-memory or SQLite test provider. |
| 20  | high     | tests       | Controllers/FoodController.cs    | 23    | `GetById` returns a bare `CatalogItem` so a missing ID serializes as an empty 204, and no endpoint in the project has any status code asserted anywhere. |
| 21  | medium   | security    | Controllers/FoodController.cs    | 30    | `CreateFood` binds `CatalogItem` with no ModelState check and no data annotations on the type, so `ID` is caller-settable and collides with the IDs 1-5 seeded by `HasData`. |
| 22  | medium   | tests       | Controllers/FoodController.cs    | 30    | Nothing asserts what a POST with a caller-supplied ID in the seeded range does. |
| 23  | medium   | performance | Controllers/FoodController.cs    | 41    | `Attach` plus `Entry(item).State = Modified` flags every property dirty, emitting a full-row UPDATE, and a PUT for a missing ID affects 0 rows and surfaces as a `DbUpdateConcurrencyException` 500 instead of a 404. |
| 24  | medium   | performance | Controllers/FoodController.cs    | 18    | The read-only GET tracks every returned entity and projects no DTO, paying a change-tracker snapshot and identity-map entry per row. |
| 25  | medium   | tests       | Controllers/FoodController.cs    | 18    | Nothing asserts a maximum page size, and the tracking cost is only reachable through `ChangeTracker` from a fixture that cannot be built today. |
| 26  | medium   | performance | Controllers/FoodController.cs    | 25    | `FirstOrDefaultAsync` runs tracked on a read-only lookup, allocating a snapshot and identity-map entry for an entity discarded at end of request. |
| 27  | medium   | security    | Common/AppBuilder.cs             | 146   | Swagger UI is mounted at the site root and wired unconditionally in all environments, publishing the full API surface to anonymous callers. |
| 28  | medium   | tests       | Common/AppBuilder.cs             | 146   | Nothing asserts what `GET /` returns in a non-Development environment. |
| 29  | medium   | tests       | Common/AppBuilder.cs             | 131   | No test asserts the `Access-Control-Allow-Origin` header the unconditional CORS policy emits. |
| 30  | medium   | security    | appsettings.json                 | 14    | The Application Insights connection string and its instrumentation key are committed in cleartext, allowing telemetry injection into the customer's workspace. |
| 31  | medium   | security    | Program.cs                       | 56    | No `UseHttpsRedirection` and no HTTPS binding, so the secret-bearing `/config` and `/config/getEnvVars` responses travel in cleartext. |
| 32  | medium   | performance | Program.cs                       | 27    | `UseSqlServer` is configured with no options lambda and therefore no `EnableRetryOnFailure`, so every transient Azure SQL fault becomes an unretried 500. |
| 33  | medium   | tests       | Common/AppBuilder.cs             | 18    | `private static bool appConfigProviderLoaded` is process-wide mutable state written in `AddConfig` and read at line 159, so two hosts in one test process share it and outcomes become order-dependent. |
| 34  | medium   | tests       | Controllers/HealthController.cs  | 13    | `private static List<string> logs` is never appended to, so the `BadRequest` branch at line 29 is unreachable and the static field leaks across tests sharing a process. |
| 35  | medium   | tests       | AppInsights/AILogger.cs          | 9     | A concrete class with non-virtual methods and no interface is injected straight into `FoodController`, so a controller unit test must construct a real `TelemetryClient` and can assert nothing about what was logged. |
| 36  | medium   | tests       | Shared/Delivery.cs               | 7     | `GetDeliveryCost` is the only pure dependency-free logic in the project, is referenced by nothing, has no test, and hardcodes `baseRate` with no injection point. |
| 37  | medium   | tests       | test-controllers.http            | 50    | The .http file is the entire test surface and asserts nothing, and its `DELETE /food/1` destroys the row its own `GET /food/1` depends on. |
| 38  | low      | security    | Controllers/FoodController.cs    | 25    | `GetById` serializes null for a missing ID instead of returning 404, letting an anonymous caller enumerate which IDs exist. |
| 39  | low      | performance | Controllers/FoodController.cs    | 23    | `GetById` is typed `Task<CatalogItem>` rather than `ActionResult<T>`, so a missing ID serializes null as 204 No Content instead of 404. |
| 40  | low      | performance | Controllers/FoodController.cs    | 17    | The hottest endpoint fires an Application Insights `TrackEvent` per request carrying the hardcoded payload `"test"`, paying allocation and ingestion cost for telemetry with no diagnostic value. |
| 41  | low      | tests       | test-controllers.http            | 32    | The POST body supplies `"id": 0` and omits `inStock` and `pictureUrl`, so even the manual smoke test never exercises the full `CatalogItem` contract. |

The three criticals in ConfigController and appsettings.json compound into one chain: auth is off by default, so an unauthenticated `GET /config` returns a live SQL admin credential over plain HTTP, and the wildcard CORS policy lets any origin fetch it.

## Contested

**Basis for the unbounded GET at Controllers/FoodController.cs:18 (security vs performance).**
security: high because anonymous reachability lifts it there, implying a performance-only read would rate medium. performance: rejected the premise, not the conclusion, holding that unbounded response size and server-side memory as a function of row count is high before you ask who is calling.
Accepted: performance's basis. Row 13 stands at high on query shape alone, and the compounding anonymous access is carried separately by row 8. security confirmed the premise was its guess at the other lens rather than performance's stated position.

**Severity of the 204-instead-of-404 on GetById (security vs tests).**
security: low, as a weak ID-enumeration disclosure vector at line 25. tests: high, because it is where "no endpoint in this project has any status code asserted" first becomes visible, at line 23.
Accepted: both, unaveraged. These are two different objects that happen to surface on one behaviour, so the disclosure vector stays low at row 38 and the coverage gap stays high at row 20. Averaging them into one number would have lost the fact that the missing assertion is the larger problem.

**Assertability of the missing UseHttpsRedirection at Program.cs:56 (security vs tests).**
security: source-read-only, no HTTP test can catch it, because launchSettings.json:17 binds http with sslPort 0. tests: `WebApplicationFactory` exercises the pipeline in-process, so "assert 200 and not 307" is a valid test.
Accepted: tests' position. security conceded outright, having reasoned about a deployed request against a box with no HTTPS listener rather than an in-process one. Severity unchanged at medium.

**Runtime consequence of the un-awaited DELETE at Controllers/FoodController.cs:51 (performance vs security and tests).**
performance: states the resulting `InvalidOperationException` as fact. security and tests: the missing await is read-verified, but the runtime consequence is inference, because no reviewer executed the DELETE.
Accepted: the security/tests framing. Row 4 is filed on what was read in the source, not on an observed exception. All three declined to run the DELETE because it would mutate the checked-in `food.db` in a working tree another session may be using, which was the right call for a read-only review. What was measured instead: `bin/Debug/net10.0/catalog-service.dll` postdates FoodController.cs, so the defect compiles clean and ships past CS4014.

**How the first DELETE test should be written (performance vs tests).**
tests: opened by asking whether the first test should pin actual behaviour. performance: assert the intended contract and let it fail until line 51 is awaited, because pinning the current behaviour codifies the bug as the contract and makes the eventual fix read as a regression.
Accepted: performance's position, with the qualification tests attached and performance accepted, that pinning current behaviour is acceptable only as an explicitly labelled quarantine test committed alongside the intended-behaviour one, never instead of it.

**Whether Program.cs:12 is a finding at all (tests, uncontested by the others but unsupported).**
No teammate raised it, and a controller-scoped lens sees correct code. tests held it at high because without a bindable entry point none of the HTTP-observable findings on any of the three lists can be covered.
Accepted: tests' position. It gates most of the remediation, so it stays at high as row 15.

**Line number for the AuthEnabled flag in appsettings.json.**
performance cited :21 throughout; security and tests each cited :22 and each corrected themselves, with security also misattributing whose error it was before tests corrected that too.
Accepted: :21. Line 20 opens the `App` block, 21 is `AuthEnabled`, 22 is `UseAppConfig`.
