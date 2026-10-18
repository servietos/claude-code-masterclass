# Orchestrate an agentic team to deliver customer data persistence

Coordinate the dotnet-expert and angular-expert as a team to add customer data persistence to the food-shop checkout page.

This lab uses the Angular frontend and the .NET catalog API for the guided steps. If you prefer React, substitute `src/food-app/shop-ui/food-shop-react` and design your own React agent using the same orchestration principles below.

## Where to Open Claude Code

This lab works against the harness this repository already ships, so open Claude Code at the repo root. It drives the committed `dotnet-expert` and `angular-expert` against the real apps under `src/`: the .NET catalog API at `src/food-app/catalog-api/catalog-service-cs` and the Angular frontend at `src/food-app/shop-ui/food-shop-ng`. Nothing this lab creates belongs in the repo's `.claude/` directory.

There is nothing to scaffold and nothing to change into: the harness this lab drives is already in this repo, so once the session opens at the repo root you are already in the right folder. Run this from wherever you cloned the repository; both commands work unchanged in PowerShell.

```bash
cd <the folder you cloned this repository into>
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open the repository folder itself as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: the usual shortcut runs the other way here. Naming an app folder in the prompt is fine, but launching the session inside one is not, because `dotnet-expert` and `angular-expert` live in this repository's own `.claude/agents/`:

```text
Use the dotnet-expert sub-agent to implement Domain/Customer.cs and the CustomersController in src/food-app/catalog-api/catalog-service-cs ....
```

That prompt only resolves from the repo root, where the two committed agents are in scope. A session launched inside `catalog-service-cs` or `food-shop-ng` sees neither, and every path in the prompts below is relative to the repo root for the same reason. Stay at the repo root from Step 1 onward.

If a step here has you write a harness file, put it in the lab's own folder, never in the repository's `.claude/`.

No step does. Every artefact this lab produces is application source: a `Customer` model, an EF Core migration, a controller, an Angular service and a component change.

---

## Running the Lab Starter

Prerequisites: the .NET 10 SDK, Node 20 or newer, and the EF Core CLI. The devcontainer in `.devcontainer/` gives you the SDK and Node, but it does not install the EF Core CLI, so install it once either way:

```bash
dotnet tool install --global dotnet-ef
dotnet ef --version
```

The project already references `Microsoft.EntityFrameworkCore.Design`, so no package needs adding. The two `cd` commands below belong to the app processes in their own terminals; your Claude Code session stays at the repo root.

Terminal 1, start the .NET catalog API:

```bash
cd src/food-app/catalog-api/catalog-service-cs
dotnet run
```

The API listens at `http://localhost:5000`. Swagger UI is mounted at the site root (`c.RoutePrefix = string.Empty` in `Common/AppBuilder.cs`), so open `http://localhost:5000/` and confirm the `Food` endpoints are listed. `http://localhost:5000/swagger` is a 404; the raw spec lives at `http://localhost:5000/swagger/v1/swagger.json`. Note the routes are generated with a capital letter: `/Food`, not `/food`.

Terminal 2, start the Angular frontend:

```bash
cd src/food-app/shop-ui/food-shop-ng
npm install
npm start
```

`food-shop-ng` ships with a committed lockfile, so `npm install` is a refresh rather than a cold resolve. The app opens at `http://localhost:4200`. Open `http://localhost:4200/food`, add at least one item to the cart, then navigate to `http://localhost:4200/food/checkout` to confirm the checkout form is visible before proceeding.

Work in the two starter folders above. The completed reference implementations live beside them as `src/food-app/catalog-api/catalog-service-cs-lab03-solution` and `src/food-app/shop-ui/food-shop-ng-solution`; open them only if you get stuck.

---

## Agent Orchestration

You will coordinate the dotnet-expert and the angular-expert to add a "Save my data" slide toggle next to the "Complete Checkout" button. When toggled on, the checkout also posts customer data to a new .NET endpoint that persists it to SQLite via Entity Framework. Read `.claude/agents/dotnet-expert.md` and `.claude/agents/angular-expert.md` before starting Step 1.

---

### Step 1: Design the Orchestration

**Goal:** Reason through how to split and sequence work between the dotnet-expert and angular-expert before writing any implementation prompt.

**Discover:**

```text
I want to coordinate two specialized agents, dotnet-expert and angular-expert, to deliver a feature
across a .NET API and an Angular frontend. Before I start, help me design the handoff.

Read .claude/agents/dotnet-expert.md and .claude/agents/angular-expert.md to understand what each
agent can do and whether its Bash access is scoped.

The feature: add a "Save my data" slide toggle next to the checkout button. When enabled, the
checkout flow also sends customer data to a new .NET API endpoint that saves it to an EF Core
SQLite table.

Answer these questions:
1. Should I run both agents in parallel or sequentially? If sequentially, which runs first and why?
2. What information does the Angular agent need that only the .NET agent can provide?
3. What should the agreed API contract look like (the URL, HTTP method, and request body
   fields) so both agents can build against the same spec?
4. What risk does running the Angular agent before the backend agent create?

Give me a short recommendation for each before I start writing prompts.
```

**What to look for:** Claude should read both agent files before answering, not guess at their capabilities. The answer to question 1 must be sequential with the .NET agent first, because the Angular agent needs the endpoint URL and request schema. Question 2 should name the API contract as the handoff artifact. Question 3 should produce a concrete URL such as `POST /api/customers` and a JSON schema listing the fields the Angular form already collects. Push back if Claude proposes parallel execution without explaining how to share the contract between agents.

On the Bash question, the honest answer is that neither agent scopes it: both `tools:` lines list a bare `Bash`, with no `Bash(dotnet ef:*)` or `Bash(npm:*)` entry and no permissions block, so both hold unrestricted Bash. Note the contrast with the minimally scoped agent you built in lab 02 and decide whether you would tighten these before running them. Both files do define the structured output contract the later steps rely on: a JSON object with `status`, `filesChanged`, `summary`, and `errors`.

**Recipe:**

```text
I am coordinating two specialized Claude agents to deliver a feature across a .NET API and
an Angular frontend. I will run them sequentially: dotnet-expert first, then angular-expert.

The API contract both agents will build against:
- Endpoint: POST /api/customers
- Request body (all strings unless noted):
  {
    "name": "string",
    "email": "string",
    "phone": "string",
    "street": "string",
    "city": "string",
    "country": "string",
    "zipCode": "string"
  }
- Success response: 201 Created with the saved entity

Step 1: Use the dotnet-expert sub-agent to implement the Customer model, EF Core registration,
and CustomersController at the endpoint above.

Step 2: After the dotnet-expert returns a success status, use the angular-expert sub-agent to add
the "Save my data" slide toggle and wire the POST to the same endpoint.

Report what each agent completed and whether the integration is ready to test.
```

> The recipe above is one possible prompt based on typical findings from the discovery above. If your conversation led to different conclusions, use those instead.

---

### Step 2: Build the Backend Endpoint

**Goal:** Use the dotnet-expert to create the Customer model, register it in EF Core, and implement the CustomersController.

**Discover:**

```text
Read the following files in src/food-app/catalog-api/catalog-service-cs before making any
recommendations:
- Infrastructure/FoodDBContext.cs
- Domain/CatalogItem.cs
- Controllers/FoodController.cs

Then answer:
1. What fields should a Customer model include to cover the customer and shippingAddress form
   groups in the Angular checkout?
2. Should the Customer record also store order items, or only customer identity and address?
3. What is the pattern this project uses for injecting FoodDBContext into a controller?
4. After adding the model and DbSet, what dotnet-ef commands are needed to create and apply
   the migration? The project has no Migrations folder yet but ships a pre-built food.db.
   What does that mean for the first migration?
```

**What to look for:** Claude should read the actual source files before answering. The field list should match what the Angular checkout form collects: name, email and phone for the customer group (the group also carries an `id` control that the Customer table does not need, since the database assigns its own key), and street, city, country, zipCode for the shippingAddress group. Ignore the third `payment` group. The controller pattern question should surface that `FoodController` is declared as `public class FoodController(FoodDBContext ctx, AILogger logger) : ControllerBase`, so primary constructor injection is the pattern to match here.

The migration commands should name `dotnet ef migrations add` followed by `dotnet ef database update` in that order. Claude should also spot the trap in the last question: with no Migrations folder present, the first migration scaffolds the whole model, including a `CreateTable` for `Food`, which collides with the shipped database.

**Recipe:**

```text
Use the dotnet-expert sub-agent to implement a customer persistence endpoint in the .NET catalog
API at src/food-app/catalog-api/catalog-service-cs.

The agent must complete these tasks:

1. Create Domain/Customer.cs with this model:
   - Id (int, primary key, auto-incremented)
   - Name (string, required)
   - Email (string, required)
   - Phone (string)
   - Street (string)
   - City (string)
   - Country (string)
   - ZipCode (string)
   - CreatedAt (DateTime, set to UtcNow on save)

2. Add a DbSet to Infrastructure/FoodDBContext.cs:
   public DbSet<Customer> Customers { get; set; }

3. Create Controllers/CustomersController.cs with one endpoint:
   POST /api/customers
   - Accepts the Customer model as the request body (using [FromBody])
   - Sets CreatedAt to DateTime.UtcNow before saving
   - Saves to the database via the injected FoodDBContext using async/await
   - Returns 201 Created with the saved entity

4. Run the EF Core migration from inside the project directory. This project has no
   Migrations folder, so the first migration recreates the whole model including the Food
   table, which collides with the shipped food.db. Move the shipped database aside first,
   then let database update rebuild it. The 5 CatalogItem seed rows come back because they
   are declared with HasData in OnModelCreating:

   mv food.db food.db.bak
   rm -f food.db-shm food.db-wal
   dotnet ef migrations add AddCustomers
   dotnet ef database update

Apply all rules from the dotnet-conventions skill at
.claude/skills/dotnet-conventions/references/conventions.md: primary constructor syntax,
XML documentation on the controller class and action, structured logging, async/await with
ConfigureAwait(false), no Console.WriteLine.

Return a JSON response using the dotnet-expert schema: status, filesChanged, summary, errors.
```

> The recipe above is one possible prompt based on typical findings from the discovery above. If your conversation led to different conclusions, use those instead.

---

### Step 3: Enhance the Angular Checkout

**Goal:** Use the angular-expert to add a "Save my data" slide toggle to the checkout form and wire the POST to the backend endpoint.

**Discover:**

```text
Read these Angular files before making recommendations:
- src/food-app/shop-ui/food-shop-ng/src/app/food/shop/checkout/checkout-form/checkout-form.component.ts
- src/food-app/shop-ui/food-shop-ng/src/app/food/shop/checkout/checkout-form/checkout-form.component.html
- src/food-app/shop-ui/food-shop-ng/src/app/food/shop/order/orders.service.ts
- src/food-app/shop-ui/food-shop-ng/src/environments/environment.development.ts

Then answer:
1. Which Angular Material component should I use for the "Save my data" toggle, and where
   should it appear relative to the "Complete Checkout" button?
2. Should the toggle be a FormControl inside the reactive form, or a standalone signal?
3. Should the POST to /api/customers go inside OrdersService, or inside a new CustomersService?
   What does the existing project pattern suggest?
4. Which base URL in the environment file should point at the .NET API endpoint?
5. If the toggle is off, should the API call be skipped entirely?
```

**What to look for:** Claude should read the checkout template and confirm that `MatSlideToggle` from `@angular/material/slide-toggle` fits the existing Material Design pattern. For the binding question, a standalone `signal(false)` is simpler than adding a form control for a non-data field; either answer is defensible, but a signal avoids polluting the form's value. 
For the service question, Claude should identify that a new `CustomersService` keeps concerns separate and that `catalogApi`, set to `http://localhost:5000` in `environment.development.ts`, is the correct base URL. `ordersApi` points at port 5002 and is not what this feature uses. Push back if Claude recommends adding the customer save logic directly inside `OrdersService`.

**Recipe:**

```text
Use the angular-expert sub-agent to add a "Save my data" toggle to the checkout form in
src/food-app/shop-ui/food-shop-ng.

The agent must complete these tasks:

1. Create src/app/food/shop/customers/customers.service.ts:
   - Inject HttpClient using inject()
   - Define a CustomerDto interface: name, email, phone, street, city, country, zipCode (all string)
   - Method saveCustomer(customer: CustomerDto): Observable<unknown>
   - POST to environment.catalogApi + '/api/customers'

2. Update checkout-form.component.ts:
   - Add saveData = signal(false)
   - Inject CustomersService using inject()
   - In completeCheckout(), before emitting the onCheckout event: if saveData() is true, call
     customersService.saveCustomer() with values from the customer and shippingAddress form
     groups. Use switchMap so the order event is emitted only after the save completes (or
     skip the save if the signal is false).
   - onCheckout is an @Output() EventEmitter, so emitting after an async save requires
     terminating the observable with subscribe() inside the component. That is an accepted
     exception to the agent's "never use subscribe() in components" rule for this one
     component. Tell the agent so explicitly, or it will push back.
   - Add MatSlideToggleModule to the component's imports array

3. Update checkout-form.component.html:
   - Add a <mat-slide-toggle> element immediately before the "Complete Checkout" button
   - Label: "Save my data"
   - Bind [checked]="saveData()" and (change)="saveData.set($event.checked)"

4. Confirm environment.development.ts sets catalogApi to http://localhost:5000. Do not change
   this value.

Follow Angular 21+ conventions throughout: inject() for DI, signal() for local state,
standalone component imports, @if and @for control flow, no constructor injection.

Return a JSON response using the angular-expert schema: status, filesChanged, summary, errors.
```

> The recipe above is one possible prompt based on typical findings from the discovery above. If your conversation led to different conclusions, use those instead.

---

### Step 4: Verify End-to-End

**Goal:** Confirm the full feature works by testing the golden path and the off-state edge case.

**Discover:**

```text
The "Save my data" toggle is now implemented across both tiers. Before calling it done, help
me design a verification plan.

1. What exact steps make up the golden path test for a successful customer save?
2. How do I verify the API was not called when the toggle is off?
3. How do I inspect the SQLite database file to confirm the row was written?
4. Is checking the browser network tab enough to verify the save, or do I need to read the
   database directly?

For each scenario, tell me the quickest verification method that does not require writing
automated tests.
```

**What to look for:** Claude should propose a concrete golden path: fill the form, toggle on, submit, then check the database. For the SQLite check, it should name a specific tool: the SQLite extension for VS Code (`alexcvzz.vscode-sqlite`) is the path of least resistance on Windows, where the `sqlite3` CLI is not present unless you installed it yourself. Push back if Claude says checking the browser network tab is sufficient; a 201 response confirms the request was sent, not that the row was written correctly. The database read is the definitive check.

**Recipe:**

```text
Walk me through verifying the "Save my data" feature using the running app at
http://localhost:4200 and the API at http://localhost:5000.

Golden path:
1. Open http://localhost:4200/food, add one item to the cart, and navigate to
   http://localhost:4200/food/checkout.
2. The form arrives pre-filled from mock data (Giro Kastil, Himmelstrasse 115, Wien).
   Overwrite the name and email with values you will recognise in the database.
3. Enable the "Save my data" toggle.
4. Open the browser DevTools Network tab, then click "Complete Checkout". Expect two
   requests: the POST to http://localhost:5000/api/customers, which is the one this lab
   verifies, and the order POST to http://localhost:5002/orders/create, which fails because
   no orders service ships with this repo. That failure is expected, and it means the
   success screen never renders. Do not treat it as a defect in your work.
5. In the Network tab, confirm the POST to http://localhost:5000/api/customers returned
   201 Created with the saved entity in the response body.
6. Open src/food-app/catalog-api/catalog-service-cs/food.db using the SQLite VS Code
   extension (alexcvzz.vscode-sqlite), or the sqlite3 CLI if you have it installed, and run:

   SELECT * FROM Customers ORDER BY CreatedAt DESC LIMIT 1;

   The row should show the name and email you entered.

Edge case (toggle off):
7. Add another item and go back to checkout.
8. Leave the "Save my data" toggle off and click "Complete Checkout".
9. Confirm the Network tab shows no POST to /api/customers at all, then re-run the SELECT
   query and confirm the row count in Customers is unchanged.

Report the result of each check.
```

> The recipe above is one possible prompt based on typical findings from the discovery above. If your conversation led to different conclusions, use those instead.
