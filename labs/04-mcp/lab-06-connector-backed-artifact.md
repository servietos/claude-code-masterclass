# Publish a Page That Reads Live Data Through a Connector

Publish an issue board that fetches fresh GitHub records through your claude.ai connector every time someone opens it, then check from a second account what it shows and who may open it.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

Duration: about 1 hour 20 minutes.

---

## Introduction

A status page you publish on Monday normally shows Monday's numbers for the rest of its life. Colleagues open it on Friday, trust it, and read stale data without knowing. You will end this lab holding a published page whose records come from the source each time it is opened, together with a log of what a second account saw.

The pattern rests on three facts from the [artifact connectors topic](../../demos/04-mcp/04-artifact-connectors/readme.md):

1. Only connectors on your claude.ai account can be called from a published page. Servers in `.mcp.json` can feed the build and are unreachable afterwards.
2. The page declares its connectors at publish time, and that declaration is the boundary of what it may call.
3. Each call runs through the account of whoever is viewing, so two viewers can see different rows, and a page like this can never have a public link.

The deliverable is a published page called "Issue Pulse Board" plus a completed `sharing-log.md`.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project folder. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root ignores anything you write here without an error.

The starter is already in this repo, so there is nothing to scaffold. You work in its sibling `connector-board-solution` folder, which keeps the starter pristine. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/04-mcp/05-artifact-connectors/connector-board-solution
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and does not follow the `cd` above. Open `connector-board-solution` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command in a plain terminal.

---

## Running the Lab Starter

The starter is `labs/04-mcp/05-artifact-connectors/connector-board`. It holds three files and no code:

| File | Purpose |
|------|---------|
| `brief.md` | The data source, fields and sections the page must show |
| `sharing-log.md` | An empty table you fill in from the second account in Step 9 |
| `results/` | Where Claude saves notes and page sources during the lab |

Before Step 1 you need:

- Claude Code v2.1.209 or later (`claude --version`), on a Pro, Max, Team or Enterprise plan. Earlier versions still produce a page, with data frozen at publish time.
- The session signed in with `/login` to the claude.ai account you will publish from.
- The GitHub connector added on that account under Settings > Connectors on claude.ai.
- A second claude.ai account you can sign in to in another browser profile or private window: a colleague's, or a spare of your own. On a Team or Enterprise plan a colleague in the same organization is ideal.

This lab never writes into the repo root and needs no installs.

---

## Step 1: Separate Reachable Servers from Unreachable Ones

**Overview:** Only some of the MCP servers your session sees can be called once a page is published. Knowing which ones before you build avoids a page whose live sections stay empty for everyone.

**Research / Planning / Discussion:**

```text
Run /mcp and list every MCP server this session can see. For each one, say whether it runs on my machine or is a connector attached to my claude.ai account, and whether a published artifact page could call it each time a viewer opens the page. Tell me which source in brief.md I would use.
```

**Finding:** A good answer sorts servers into two groups. Local stdio servers and remote servers registered through `.mcp.json` can supply data while Claude builds the page and cannot be called after publishing. Claude-ai connectors are the only ones a viewer's page load can reach. If the GitHub connector is missing from the list, stop and add it on claude.ai, then run `/login` again before continuing.

**Recipe:**

```text
Read brief.md in this folder. Then write results/connector-check.md with a table of every MCP server visible in this session, one row each, with columns: Server, Where it runs, Callable from a published page (yes or no), Reason. End the file with one line naming the connector the Issue Pulse Board will declare.
```

**Expected Outcome:** `results/connector-check.md` exists with one row per server. The GitHub connector is marked callable from a published page, and every locally registered server is marked not callable. The closing line names the GitHub connector.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Plan the Calls Before Building

**Overview:** A live page is a small client: every section is a connector call made at view time. Planning the calls first shows which sections can share one request and which fields the connector can actually return.

**Research / Planning / Discussion:**

```text
Read brief.md. For each section in it, list the connector call that would fill it at view time, which fields that call returns, and whether any section can reuse the result of another call. Flag any field in the brief the connector cannot supply. Do not build anything yet.
```

**Finding:** Look for a plan where "Latest issues" and "Label counts" share one list call, because the counts derive from the same 10 records. A good answer names a concrete GitHub tool for the list call and says where the "Data as of" time comes from (the moment of each call). Push back if Claude proposes typing sample rows into the page "for layout"; the quality bar in `brief.md` rules that out.

**Recipe:**

```text
Read brief.md and write results/call-plan.md. For each section list: the connector tool it calls, the arguments, the fields used, and what the section shows when the call fails. Mark which sections share a call. Do not build the page.
```

**Expected Outcome:** `results/call-plan.md` lists at most two connector calls. The Header, Latest issues and Label counts sections each have a failure behaviour written down.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 3: Publish a Frozen Baseline

**Overview:** To see what live data buys you, first publish the version every artifact produces by default: records fetched once during the build and baked into the page. This is the control you compare against later.

**Recipe:**

```text
Build an artifact page titled "Issue Pulse Board (frozen)" following brief.md. Fetch the 10 most recently updated open issues of anthropics/claude-code now through my GitHub connector and write them into the page as static content. Do NOT make the page call any connector when it loads. Show a "Data as of" line with the time of this build. Save the page source to results/board-frozen.html and publish it.
```

**Expected Outcome:** Claude calls the GitHub connector while building, then publishes and prints a `claude.ai/code/artifact/...` URL. Open it: the 10 issues and the label counts appear, and the "Data as of" line shows the build time. Reload the page and nothing changes. Write down the URL and the time shown.

---

## Step 4: Publish the Live Board

**Overview:** The live version differs in one decision: the connector is declared at publish time and the page calls it on each load. Claude asks you to approve that declaration, and the approval screen is the security boundary made visible.

**Recipe:**

```text
Build a second artifact page titled "Issue Pulse Board" following brief.md and results/call-plan.md. The page must fetch the 10 most recently updated open issues of anthropics/claude-code live through my GitHub connector each time it loads, in the browser, as the viewer. Do not write any issue data into the page source. Fill the "Data as of" line from the time of each call. Save the page source to results/board-live.html and publish it as a new artifact.
```

**Expected Outcome:** Before publishing, an approval names the GitHub connector as the one the page may call. After you approve, Claude prints a second URL. Opening it shows the same kind of content as the frozen page, and the first view may present a permission ask from claude.ai asking whether the page may use your GitHub connector. Allow it once.

> **Note:** If the approval never names a connector, the page was published as a static page. Ask Claude to republish and state the connector it declared.

---

## Step 5: Prove the Data Is Live

**Overview:** A page that looks right proves little. The check is behavioural: the stamp moves on reload and the live page diverges from the frozen one as the repository changes.

**Research / Planning / Discussion:**

```text
I have two published pages: "Issue Pulse Board (frozen)" and "Issue Pulse Board". What observations would prove the second one reads live and the first does not? Give me three checks I can run in a browser in under two minutes, and say what each result means.
```

**Finding:** Good checks include reloading each page and watching the "Data as of" line, comparing the first row of both pages (the repository is busy, so the live page usually gains newer issues within minutes), and viewing the page source or network panel for the connector request. A check that only compares layout proves nothing.

**Recipe:**

```text
Read results/board-frozen.html and results/board-live.html. Write results/live-proof.md with two sections. In the first, quote the exact lines in each file that decide whether issue data is baked in or fetched at load. In the second, list the "Data as of" text I should expect to see on each page after a reload.
```

**Expected Outcome:** Reload the live page twice: the "Data as of" stamp moves each time. Reload the frozen page: the stamp stays at the build time from Step 3. `results/live-proof.md` quotes the connector call in `board-live.html` and shows no issue titles in that file.

---

## Step 6: Add a Refresh Control and an Interval

**Overview:** A page left open on a second monitor goes stale again. A refresh control and an interval make the freshness something the viewer can see and trigger.

**Recipe:**

```text
Update the live "Issue Pulse Board" artifact. Add a Refresh button in the header that refetches from the GitHub connector and updates the "Data as of" line. Also refetch automatically every 5 minutes while the page is open. While a fetch is running, show "Refreshing" next to the button. Keep the connector declaration unchanged. Save the source to results/board-live.html and republish to the same URL.
```

**Expected Outcome:** The same URL now shows a Refresh button in the header. Press it and the "Data as of" stamp changes to the time of the press. Reload the whole page: the board makes a new connector call and the "Data as of" stamp shows the time of that load.

---

## Step 7: Give Every Live Section a Fallback

**Overview:** Connectors are per account. A viewer without the GitHub connector, or one who declines the permission ask, must see which connector to add.

**Research / Planning / Discussion:**

```text
List every way a live section of Issue Pulse Board can end up with no data for a viewer: connector missing, permission declined, connector returns an error, connector returns zero issues. For each, say what the viewer should read on the page, and which of those the page can tell apart from each other.
```

**Finding:** Three distinct messages are the target. A good answer separates "you have no connector or declined" from "the call failed" from "the call worked and returned nothing", because each has a different fix. Reject a single generic "no data" line.

**Recipe:**

```text
Update the live "Issue Pulse Board" artifact. Add a fallback to the Latest issues section and to the Label counts section. The fallback must name the GitHub connector as the connector needed, link to Settings > Connectors on claude.ai, and distinguish: connector missing or ask declined, call failed, and call succeeded with zero issues. Keep the data fetching unchanged. Save the source to results/board-live.html and republish to the same URL.
```

**Expected Outcome:** The page behaves as before for you. The fallback text is present in `results/board-live.html`, with three distinct messages per section. You will see them from the second account in Step 9.

---

## Step 8: Read the Declaration Back

**Overview:** The declared connector list is what limits the page. Reading it back from the published artifact turns a claim into evidence you can show a security reviewer.

**Recipe:**

```text
Read my published "Issue Pulse Board" artifact. Report: the connectors it declares, every connector tool the page code calls, and whether any call targets a connector that is not declared. Then tell me what would happen if I asked you to add a section that reads my calendar, and what I would have to do before that section could work. Write the answers to results/declaration.md.
```

**Expected Outcome:** `results/declaration.md` lists the GitHub connector as the only declared connector and the list-issues tool as the only call. It states that a calendar section needs the calendar connector added to the declaration and a republish with a fresh approval; a page cannot reach beyond its declaration on its own.

---

## Step 9: Open the Page from a Second Account

**Overview:** Everything so far ran as you. This step shows the part that surprises people: the call runs as the viewer, and the sharing options are narrower than for a plain artifact. Open `sharing-log.md` and fill one row per scenario.

1. In a different browser profile or private window, sign in to claude.ai with the second account.
2. Paste the live "Issue Pulse Board" URL from Step 4.
3. Run the four scenarios below in order, filling `sharing-log.md` after each.

| Scenario | How to set it up |
|----------|------------------|
| Second, connector added | Add the GitHub connector on the second account, then open the page and allow the permission ask |
| Second, ask declined | Reload, then decline the permission ask |
| Second, connector missing | Remove the GitHub connector from the second account, then open the page |
| Primary | Reopen the page as yourself and note the plan you are on |

**Recipe:**

```text
Read sharing-log.md. I will paste my observations scenario by scenario. After each one, update the matching row and tell me which of the three causes in the artifact connectors topic readme explains what I saw, using the symptom table in demos/04-mcp/04-artifact-connectors/readme.md.
```

**Expected Outcome:** For the added connector, the second account sees a permission ask, then a board populated from its own GitHub access, with a "Data as of" stamp of its own. After declining, the live sections show the fallback text from Step 7 and the rest of the page still renders. With the connector missing, the fallback names the GitHub connector and points to Settings > Connectors. Your Share control offers no public link, and the plan row records whether sharing inside an organization is possible on your plan.

> **Warning:** The decline lasts for that page load. Reload the page to bring the ask back.

---

## Step 10: Write the Handover Note

**Overview:** The point of the lab is a pattern you can repeat for any tracker on any connector. Capture the checks you ran as a short note a colleague could follow.

**Recipe:**

```text
Read results/connector-check.md, results/call-plan.md, results/live-proof.md, results/declaration.md and sharing-log.md. Write results/handover.md with: the URL of the live board, the connector it declares, the three checks that prove the data is live, the four viewer cases and what each sees, and the sharing limits that apply on my plan. Keep it to one page.
```

**Expected Outcome:** `results/handover.md` links the live URL, names the GitHub connector, and lists the viewer cases from `sharing-log.md`. It states that the page cannot have a public link.

---

## Verify

1. The live URL loads and its "Data as of" stamp changes on every reload and every press of Refresh.
2. `results/board-live.html` contains the connector call and none of the issue titles that the page displays. Pick one displayed title and search the file for it.
3. The frozen page's stamp still shows the build time from Step 3.
4. `sharing-log.md` has every row filled in from the second account.

---

## Cleanup

Both artifacts are private to your account. Remove them once you have finished comparing:

```text
Delete the artifacts "Issue Pulse Board (frozen)" and "Issue Pulse Board". Confirm each deletion with me first.
```

Remove the GitHub connector from the second account if you added it only for this lab.
