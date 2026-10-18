# Serve the Same Document Generator to Clients That Are Not Claude

A skill's renderer is ordinary code, so the capability does not have to stay inside Claude Code. Put an HTTP endpoint in front of the same module and your billing system, your CRM, or a colleague with `curl` can generate the identical document, while the skill keeps calling it locally.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

The completed reference lives in [invoice-api-solution/](invoice-api-solution). Work in the pristine starter [invoice-api/](invoice-api) and open the solution only when you want to compare.

---

## Where to Open Claude Code

This lab builds a service around the lab project's own renderer, so open Claude Code inside the lab folder rather than at the repository root. `npm install`, `npm run render`, `npm start` and the `curl` calls below all resolve against the directory the session was launched in, and the repo root carries no `package.json` at all, so a session opened there cannot install the dependency or start the server.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/03-skills/invoice-api
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `invoice-api` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/03-skills/invoice-api refactor scripts/render.mjs so it exports a buffer-returning function ....
```

That works for any step whose result is just files, which here is every one of them: this lab writes no harness pieces, no `.claude/skills/`, no hooks in `.claude/settings.json` and no `.mcp.json`, and Step 4 only writes a decision note rather than editing the lab 01 skill. What the shortcut does not fix is the working directory, so `npm install`, `npm start` and the `curl` in Step 3 still have to run inside the project. Launch inside the starter from Step 1 onward.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and are read from the repo root. You read from them without ever writing into them, and every path in the prompts below is relative to the lab folder.

The starter is self-contained: it already ships `scripts/render.mjs`, the finished renderer from [lab 01](lab-01-invoice-docx-skill.md), plus the sample data. Run this lab whether or not you did that one.

---

## Setup

```bash
npm install
npm run render
```

`out/invoice.docx` appears. That proves the renderer works before any HTTP is involved, which is the state you want when the endpoint later returns something unreadable.

---

## Step 1: Decide What the Endpoint Returns

**Overview:** A document endpoint has one real design decision, and getting it wrong is what makes generated files arrive corrupted.

**Research / Planning / Discussion:**

```text
I want to expose scripts/render.mjs as an HTTP endpoint that takes invoice JSON and
returns a Word document.

1. Should the response body be the .docx bytes, a base64 string, or a URL to a stored file?
   Give the trade-off of each and recommend one for a service called by another program.
2. Which Content-Type and Content-Disposition headers does a .docx response need, and what
   goes wrong in the client if either is missing or wrong?
3. My renderer currently reads argv and writes a file. What has to change so the same code
   serves both the CLI and the endpoint without duplicating the layout?
```

**Finding:** For a program-to-program service the bytes are the right answer, with the OpenXML wordprocessingml Content-Type and a `Content-Disposition` filename; a wrong or missing Content-Type is exactly how a downloaded file ends up unopenable. On the third question the answer should be to export the builder as a function and keep the argv handling behind a guard, so the CLI path and the HTTP path share one layout definition rather than two copies that drift.

**Recipe:**

```text
Refactor scripts/render.mjs so it works as both a module and a CLI:
- Export a function that takes the invoice object and resolves to a document buffer
- Keep the existing argv behaviour, but only when both arguments are present
- Do not change the layout or the arithmetic

Confirm afterwards that npm run render still produces an identical document.
```

**Expected Outcome:** `npm run render` still writes a working `out/invoice.docx`, and the module now exports a buffer-returning function that something else can import.

---

## Step 2: Put the Endpoint In Front of It

**Overview:** Wrap the exported renderer in the smallest possible HTTP surface: one health route and one document route.

**Research / Planning / Discussion:**

```text
Before writing the server: what belongs in an invoice endpoint and what does not?
For each of these, say in or out and why: request body validation, authentication,
persisting the generated file, an invoice-number sequence, a health route.
Assume this runs on a laptop today and behind a real gateway later.
```

**Finding:** Validation and a health route are in, since both are cheap and both are how you tell a bad request from a broken service. Authentication belongs at the gateway rather than hand-rolled here, but the answer should say that explicitly rather than ignore the question. Persistence and number sequences are separate concerns that would turn a stateless renderer into a system of record.

**Recipe:**

```text
Create server.mjs with Express:
- GET /health returns { "status": "ok" }
- POST /invoices takes invoice JSON, renders it with the exported function, and returns
  the .docx bytes with the OpenXML Content-Type and a Content-Disposition filename
  built from the invoice number
- Port from process.env.PORT with a default of 3200
- Add a start script to package.json

Keep it to one file and no error middleware.
```

**Expected Outcome:** `npm start` prints the listening address, and `curl http://127.0.0.1:3200/health` answers `{"status":"ok"}`.

---

## Step 3: Generate a Document Over HTTP and Prove It Opens

**Overview:** A 200 response is not proof. The document has to be a real OpenXML package, which is worth checking rather than assuming.

**Research / Planning / Discussion:**

```text
How do I verify that a .docx returned by an HTTP endpoint is genuinely valid, without
opening Word? Give me two checks: one on the response itself and one on the saved file.
Explain what a corrupted response would look like in each check.
```

**Finding:** On the response, the status plus the Content-Type and a plausible byte count. On the file, that a `.docx` is a ZIP container: listing its entries should show `word/document.xml` among roughly twenty parts. A corrupted or JSON-error response fails the ZIP check immediately, which is why it beats eyeballing the size.

**Recipe:**

```text
With the server running, post the sample invoice and save the result:

curl -s -X POST http://127.0.0.1:3200/invoices \
  -H "Content-Type: application/json" \
  -d @data/invoice-sample.json \
  -o out/api-invoice.docx -w "http %{http_code} %{size_download} bytes\n"

Then confirm the saved file is a valid OpenXML package by listing its ZIP entries and
showing that word/document.xml is present. Report the number of parts.
```

**Expected Outcome:** HTTP 200 with roughly nine kilobytes returned, and the ZIP listing shows about twenty-two parts including `word/document.xml`. The file opens in Word with the same three line items and the same totals as the CLI render.

---

## Step 4: Point the Skill at the Service

**Overview:** Now the interesting part: the skill from lab 01 can call the endpoint instead of shelling out, which is what turns a personal skill into a shared capability.

**Research / Planning / Discussion:**

```text
My invoice-docx skill currently runs a local Node script. If it posted to this endpoint
instead:

1. What changes in the skill's allowed-tools, and what new failure mode appears that the
   local script did not have?
2. When is the local script the better choice, and when is the service?
3. If both paths exist, how should the skill decide which to use, without asking me
   every time?
```

**Finding:** The tool set moves from `Bash(node:*)` toward a network call, and the new failure mode is the service being down or unreachable, which the local path could not suffer. The honest answer on the second question is that the local path wins for a single user and the service wins when other systems need the same documents. On the third, a configured base URL with a local fallback beats asking, and the decision belongs in the skill body rather than in the renderer.

**Recipe:**

```text
Write a short decision note, under 20 lines, for the invoice-docx skill: when it should
render locally, when it should post to the invoice API, how it picks, and which
allowed-tools entry each path needs. Do not modify the skill yet.
```

**Expected Outcome:** A written decision note you could paste into `SKILL.md`. It names a concrete rule for choosing a path, not a preference, and it is explicit about which tool each path requires.
