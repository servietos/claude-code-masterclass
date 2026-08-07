# Drive an Interactive PDF Viewer with MCP Apps

Use the PDF MCP server to open, navigate, annotate and save product manuals directly inside Claude Desktop's embedded viewer.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

---

## Introduction

This lab explores the PDF server, an MCP App that embeds an interactive PDF viewer directly in Claude Desktop. Unlike a plain tool that returns text, an MCP App renders a full UI inside the host. You will experience five capabilities the PDF server demonstrates:

1. **Chunked streaming**: large PDFs load in chunks via HTTP Range requests so no single tool response exceeds size limits.
2. **Model context updates**: every page turn pushes current page text to the model so Claude can answer questions about what you are reading.
3. **Fullscreen display mode**: the viewer requests fullscreen from Claude Desktop for an immersive reading experience.
4. **Interact tool**: a command queue lets Claude navigate, annotate, search, fill forms and save without you having to touch the viewer manually.
5. **Annotation export**: annotations are stored as real PDF annotation dictionaries so they survive in any PDF reader.

The PDF server runs over stdio, which means it launches as a subprocess of the host and the `interact` tool is always enabled (over HTTP it takes an explicit `--enable-interact` flag).

**Host requirement, stated plainly:** the embedded viewer is an MCP App webview. Only an MCP App-aware host renders it, and Claude Desktop is the one this lab targets. In Claude Code you can list the tools and call them, but nothing renders: `display_pdf` returns a `viewUUID`, `interact` answers `Queued: ...` and the queued command waits for a viewer that never polls.

Steps 1 to 6 below therefore assume a running Claude Desktop with the server registered. `read_pdf_text` is the exception; it extracts text server-side and works in any host.

---

## Where to Open Claude Code

This lab works against the harness this repository already ships, so open Claude Code at the repo root. It configures Claude Desktop rather than this project, so the only registration you write lands in Claude Desktop's own config file, while the repo-root `.mcp.json` already carries the `pdf` entry that makes the tools visible in Claude Code. Nothing this lab creates belongs in the repo's `.claude/` directory.

The session belongs at the repo root, so you are already in the right folder: there is nothing to scaffold and nothing to change into beyond the clone itself. Both commands work unchanged in PowerShell.

```bash
cd <the folder you cloned this repository into>
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `claude-code-masterclass` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: naming a path in the prompt instead of switching folders is the usual shortcut, and here it runs the other way round, because the session already sits at the root:

```text
In labs/04-mcp/03-mcp-app/pdf-server run npm install and npm run build, then confirm dist/index.js exists ....
```

That works for any step whose result is just files, such as the build above. It does not work in reverse: the `pdf` entry lives in the repo-root `.mcp.json`, which loads from the directory the session was launched in, so a session started inside `pdf-server` sees no `pdf` server and none of its tools. Launch at the repo root from Step 1 onward.

If a step here has you write a harness file, put it in the lab's own folder, never in the repository's `.claude/`. No step does: the only configuration you edit is `claude_desktop_config.json`, never the repository's `.claude/` or `.mcp.json`.

---

## Running the Lab Starter

The starter project is `labs/04-mcp/03-mcp-app/pdf-server`. The finished reference lives beside it at `labs/04-mcp/03-mcp-app/pdf-server-solution`: same sources, with dependencies installed and `dist/` already built. Work in the starter and open the solution only to compare.

### What the build requires

Node.js 20 or newer, plus **Bun**: the build ends in three `bun build` passes, and `src/pdf-annotations.test.ts` imports `bun:test`, so the `tsc --noEmit` stage needs Bun's ambient types too. Both are declared as devDependencies (`bun` and `@types/bun`), so `npm install` provides them locally and no global install is needed. Open a terminal in the `labs/04-mcp/03-mcp-app/pdf-server` folder:

```bash
npm install
npm run build
```

The build type-checks, bundles the viewer UI into `dist/mcp-app.html` with Vite (about 4.7 MB, the PDF.js runtime is inlined), then emits `dist/pdfjs-polyfill.js`, `dist/server.js` and `dist/index.js` (about 1.1 MB) with Bun. `dist/` is git-ignored and never checked in, so the build must complete before `dist/index.js` exists.

### Run the server manually first

Start it directly from a terminal to confirm it launches before you wire it into a host:

```bash
node dist/index.js --stdio
```

It prints one line to stderr and then waits on stdin for JSON-RPC messages, exactly as the host will drive it:

```text
[pdf-server] Ready (1 URL(s) configured)
```

The one configured URL is the built-in default document (`https://arxiv.org/pdf/1706.03762`), not a file of yours. Stop it with `Ctrl+C`.

To expose local PDF files, pass a directory as a trailing argument:

```powershell
node dist/index.js --stdio "C:\Users\me\Documents"
```

```bash
node dist/index.js --stdio ~/Documents
```

The server then logs `[pdf-server] Registered local directory: ...` and `list_pdfs` answers with `Allowed local directories:` followed by the path. Without that argument, `list_pdfs` returns exactly one line, `Any remote PDF accessible via HTTPS can also be loaded dynamically.`, which is correct behaviour.

---

## Setup: Register the PDF MCP Server

The config file is `%APPDATA%\Claude\claude_desktop_config.json` on Windows and `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS. In Claude Desktop, **Settings > Developer > Edit Config** opens (and creates) that exact file.

Register the server you just built, using an absolute path to `dist/index.js`:

```json
{
  "mcpServers": {
    "pdf": {
      "command": "node",
      "args": [
        "D:\\git-customers\\claude-code-masterclass\\labs\\04-mcp\\03-mcp-app\\pdf-server\\dist\\index.js",
        "--stdio"
      ]
    }
  }
}
```

On macOS or Linux the same entry uses a forward-slash path such as `/Users/me/claude-code-masterclass/labs/04-mcp/03-mcp-app/pdf-server/dist/index.js`. Restart Claude Desktop after saving; the PDF tools appear in a new conversation.

### The published package as an alternative

A prebuilt copy of this server is on npm, so `npx` runs it without any local build. Use this entry in `claude_desktop_config.json` in place of the local-build one above:

```json
{
  "mcpServers": {
    "pdf": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "--silent",
        "--registry=https://registry.npmjs.org/",
        "@modelcontextprotocol/server-pdf",
        "--stdio"
      ]
    }
  }
}
```

The same entry is already present in `.mcp.json` at the repo root, which is what makes the `pdf` tools available in Claude Code: that file is committed and needs no change from you. Be aware of one real difference: the published build exposes **three** model-visible tools (`list_pdfs`, `display_pdf`, `interact`) and does **not** contain `read_pdf_text`. Only the locally built server in this repo exposes all four, so Step 5's server-side text extraction needs the local build.

---

## Step 1: Display a Product Manual in the Embedded Viewer

**Overview:** Open a product manual in the interactive PDF viewer and observe the chunked loading and auto-fullscreen behaviour. Because the server was started with no local file arguments, `list_pdfs` returns no local files, only the message that any HTTPS URL can be loaded. We supply the URL directly.

**Research / Planning / Discussion:**

```text
What PDF tools does this MCP server expose? List each tool name and describe what it does. Before I open any document, I want to understand the available capabilities.
```

**Finding:** Against the locally built server, a good response names four model-visible tools: `list_pdfs`, `display_pdf`, `interact` and `read_pdf_text`. Claude should explain that `display_pdf` opens a URL in the embedded viewer, `list_pdfs` reports which local directories are allowed, `read_pdf_text` extracts text server-side, and `interact` sends commands through the viewer's command queue. Six further tools exist (`read_pdf_bytes`, `submit_page_data`, `submit_save_data`, `submit_viewer_state`, `poll_pdf_commands`, `save_pdf`) but are marked app-only, so the model never sees them; the viewer calls them. If you registered the published npm package instead, `read_pdf_text` is legitimately absent: that is the package, not your config.

**Recipe:**

```text
Use the PDF MCP server to display the JBL Charge 5 quick start guide. The URL is https://www.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dw758fd8f3/pdfs/PA_JBL_Charge%205_QSG_Global.pdf. Show it in the viewer.
```

**Expected Outcome:** Claude calls `display_pdf` with the JBL URL. In Claude Desktop the embedded viewer opens, requests fullscreen and loads the manual page by page with a progress indicator; the toolbar shows page navigation, zoom controls and an annotations button. The tool response itself carries no title and no page count: it returns the text `PDF opened. viewUUID: <uuid>`, a structured payload of `{ viewUUID, url, initialPage: 1, totalBytes: 2022918 }` and `_meta` of `{ viewUUID, interactEnabled: true, writable: false }`. Claude should report the `viewUUID` and the source URL; the page count only becomes known once the viewer submits page data, or immediately from `read_pdf_text`, which reports `(2 pages total)`.

The response also warns Claude not to call `display_pdf` a second time, because that spawns a separate viewer with a different `viewUUID`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Navigate and Search

**Overview:** Use Claude to drive the viewer to a specific page and search for a term, demonstrating the command-queue-based interact tool.

**Research / Planning / Discussion:**

```text
The PDF viewer is currently showing page 1 of a document. What interact actions are available for navigating between pages and searching for text? Describe what parameters each action takes.
```

**Finding:** A good response identifies `navigate` with a `page` parameter and `search` with a `query` parameter, out of the 14 actions the schema allows (`navigate`, `search`, `find`, `search_navigate`, `zoom`, `add_annotations`, `update_annotations`, `remove_annotations`, `highlight_text`, `fill_form`, `get_text`, `get_screenshot`, `get_viewer_state`, `save_as`). Claude should explain that every call carries the `viewUUID` returned by `display_pdf`, and that several commands can be batched in one call through the `commands` array. If Claude only mentions scrolling or clicking rather than named action strings, ask it to consult the tool schema directly.

**Recipe:**

```text
Go to page 2 of the manual currently open in the PDF viewer. Then search for the term "Bluetooth" and tell me how many times it appears.
```

**Expected Outcome:** Claude calls `interact` with `action: "navigate"` and `page: 2`, and the tool answers `Queued: navigate to page 2`. It then calls `interact` with `action: "search"` and `query: "Bluetooth"`. In Claude Desktop the viewer picks the queued commands up on its next poll, jumps to page 2, scrolls to the first match and shows the match count, which Claude reports back. Without a live viewer the commands stay queued and nothing happens, which is the clearest demonstration in this lab that the app half of an MCP App is doing real work.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 3: Annotate with Highlights and Notes

**Overview:** Ask Claude to mark up the manual with highlights and sticky notes, showing how annotation instructions flow through the command queue.

**Research / Planning / Discussion:**

```text
What annotation types can be added to a PDF through the interact tool? Describe the parameters for highlight and note annotations, and how the command queue processes them.
```

**Finding:** A good response describes `highlight_text` (parameters `query`, optional `page`, `color`, `content`), which finds the text itself, and `add_annotations`, which takes an array of annotation objects that each need `id`, `type` and a 1-indexed `page`. For a `note` the extra fields are `x`, `y`, `content` and an optional `color`. Claude should state the coordinate system: PDF points at 72 per inch, origin at the page **top-left**, x increasing rightward and y increasing downward, with US Letter at 612 x 792 points and a top margin around `y = 50`.

It should also note that commands are queued and applied in order. If Claude conflates annotation types or cannot describe the coordinate origin, review the tool description before sending annotation commands.

**Recipe:**

```text
On the current page of the open PDF, highlight every step in the Bluetooth pairing instructions. Then add a sticky note at the top of the page with the text "Pairing, check this first".
```

**Expected Outcome:** Claude prefers `highlight_text` over hand-built rectangles because it locates the text itself, then calls `add_annotations` with a note such as `{ id: "n1", type: "note", page: 1, x: 72, y: 50, content: "Pairing, check this first" }`. Each call answers with a `Queued: ...` line. In Claude Desktop yellow highlight overlays appear over the matched text, a note icon appears at the given point and the annotations badge updates. Note that this quick start guide is a pictorial layout: the pairing steps are mostly icons with short labels, so expect fewer highlight hits than in a prose document.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Stamp the Document and Check for Form Fields

**Overview:** Place a stamp on a page and find out whether the document has fillable fields, exercising two more parts of the interact surface.

**Research / Planning / Discussion:**

```text
What parameters does a stamp annotation take, and how are its position and colour expressed? Separately: where does a PDF's fillable form field metadata actually surface in this server's responses?
```

**Finding:** A good response explains that stamps go through `add_annotations` with `type: "stamp"` and the fields `id`, `page`, `x`, `y`, `label` (any text, for example `APPROVED`, `DRAFT`, `CONFIDENTIAL`), plus optional `color` and `rotation`, where `x, y` is the **top-left** corner of the stamp in PDF points. On forms, the accurate answer is that field metadata arrives with `display_pdf`: its structured output includes a `formFields` array when the document has any, and its text output then lists them under `Form fields available for fill_form:`. `fill_form` is the interact action that writes values, taking a `fields` array of `{ name, value }`.

`get_viewer_state` is a live-viewer snapshot (`currentPage`, `pageCount`, `zoom`, `displayMode`, `selectedAnnotationIds`, `selection`) and reports nothing about form fields. If Claude points at `get_viewer_state` for form discovery, ask it to re-read both output schemas.

**Recipe:**

```text
Add a "REVIEWED" stamp in the top-right corner of page 1 of the open PDF. Use a green colour. Then tell me whether this PDF has any fillable form fields.
```

**Expected Outcome:** Claude calls `interact` with `action: "add_annotations"` and a stamp such as `{ id: "s1", type: "stamp", page: 1, x: 430, y: 50, label: "REVIEWED", color: "#00A000" }`, and the tool answers `Queued: ...`. A green stamp appears near the top-right of page 1 in the Claude Desktop viewer. For the form question, Claude should look back at the `display_pdf` response: it contains no `formFields` entry and no `Form fields available for fill_form:` line for this quick start guide, so the correct answer is that the document has no fillable fields.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 5: Extract Page Text and Get a Screenshot

**Overview:** Have Claude retrieve the raw text and a rendered screenshot of specific pages, demonstrating server-side text access and client-side screenshot capture.

**Research / Planning / Discussion:**

```text
What does the interact tool's get_text action return, and how do you specify a range of pages? What does get_screenshot return, and how does read_pdf_text differ from both?
```

**Finding:** A good response explains that `get_text` takes either a single `page` or an `intervals` array of `{ start, end }` objects (`[{}]` means all pages, capped at 20) and returns plain text for those pages, while `get_screenshot` requires a `page` and returns that page rendered as a PNG, which is what lets Claude describe diagrams and figures. The sharpest answer also separates the transports: `get_text` and `get_screenshot` are viewer commands that need a live app, whereas `read_pdf_text` parses the file server-side and answers immediately in any host. If Claude cannot describe the `intervals` structure or treats `get_screenshot` as identical to `get_text`, ask it to re-examine the tool schema.

**Recipe:**

```text
Give me the extracted text from pages 1 and 2 of the open PDF. Also take a screenshot of page 1 and describe what diagrams or figures appear on it.
```

**Expected Outcome:** The JBL quick start guide has exactly two pages, so ask for both: Claude calls `get_text` with `intervals: [{ start: 1, end: 2 }]` (or `read_pdf_text` with the same intervals, which answers with the header `PDF: <url> (2 pages total)` followed by `--- Page 1 ---`). Page 1 is the pictorial quick start, `WHAT'S IN THE BOX`, Bluetooth pairing, PartyBoost, IP67 and charging icons, followed by the `TECH SPEC` block that repeats in a long run of languages. Claude then calls `get_screenshot` with `page: 1` and describes the speaker illustrations, the phone Bluetooth settings mock-up and the charging diagram. The screenshot needs the Claude Desktop viewer; the text does not.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 6: Save the Annotated PDF

**Overview:** Save the annotated version of the document, confirming that annotations are written as real PDF annotation dictionaries.

**Research / Planning / Discussion:**

```text
How does the PDF server handle saving annotations? What is the difference between the save_as interact action and the save_pdf app-only tool? What format are annotations stored in the saved file?
```

**Finding:** A good response distinguishes the `save_as` interact action, which is queued for the viewer and takes an absolute `path` (or `file://` URL) plus `overwrite: true` when the target exists or when `path` is omitted to overwrite the original, from the app-only `save_pdf` tool, which is marked with `ui.visibility: ["app"]` and is called by the viewer itself rather than by the model. Claude should explain that annotations are written as `/Type /Annot` dictionaries in the PDF binary, not as DOM overlays, so they persist in any PDF reader. If Claude describes annotations as view-only overlays or cannot explain the two save paths, review the tool description before proceeding.

**Recipe:**

```text
Save the annotated version of the PDF currently open in the viewer to my Documents folder so I have a copy with the highlights, note and stamp we added.
```

**Expected Outcome:** Claude calls `interact` with `action: "save_as"`, an absolute `path` and `overwrite: true` if the file already exists. The command is queued, the Claude Desktop viewer flushes the annotated bytes and the file lands at that path. Opening it in any PDF reader (Acrobat, Preview, Chrome) shows the highlight, note and stamp intact because they are `/Type /Annot` dictionaries in the file. Without a live viewer this call queues and never completes, so treat a hanging `save_as` as a missing host, not a broken server.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Running and Testing the PDF Server

### 1. Build and launch the server

```bash
npm install
npm run build
node dist/index.js --stdio
```

You should see `[pdf-server] Ready (1 URL(s) configured)` on stderr and the process should stay alive waiting on stdin. If Node.js is missing or older than 20, it fails here. Stop it with `Ctrl+C`: Claude Desktop launches its own managed instance from the config in the Setup section.

### 2. Connect to Claude Desktop

This part needs Claude Desktop installed; there is no CLI substitute for the webview. After saving the config and restarting the app:

1. Click the MCP icon (plug or hammer icon) in the chat input bar.
2. Confirm `pdf` appears in the active servers list with no error badge.
3. Start a new conversation and ask: `What PDF tools do you have available?`

Against the local build, Claude should list four tools: `list_pdfs`, `display_pdf`, `interact` and `read_pdf_text`. Against the published npm package it lists three, without `read_pdf_text`. If `interact` is missing in either case, the `--stdio` argument is absent or an HTTP transport key is overriding it.

### 3. Verify end-to-end

The lab steps above are your end-to-end test. Work through Steps 1 to 6 in Claude Desktop in order using the JBL Charge 5 manual. Each step exercises a different layer:

- Step 1 confirms the viewer renders and enters fullscreen.
- Step 2 confirms the stdio interact command queue is live (page navigation and search happen without any click).
- Steps 3 and 4 confirm annotation commands flow through to the viewer.
- Step 5 confirms text extraction and screenshot capture.
- Step 6 confirms annotated PDF export.

If every step produces its expected result, every layer of the server (chunked loading, model context updates, fullscreen display, interact tool and annotation export) is working correctly.

---

> **Note: publishing for wider access**
>
> The stdio transport means the server process lives on the same machine as the client. To make the PDF server reachable from any Claude client (Claude.ai, the API or remote teammates), you would host it over HTTP and configure clients with `"type": "http"` pointing at your endpoint. In HTTP mode `interact` is off unless you pass `--enable-interact`, and the command queue is in-memory per process, so a load-balanced multi-instance deployment drops commands: keep it to a single long-lived instance. If you extend this server, publishing your build to npm makes it as easy for others to adopt as the bare `npx` config shown above.
