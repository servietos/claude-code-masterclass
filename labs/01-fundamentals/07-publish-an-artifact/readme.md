# Publish a CI Failure Page and Revise It Through Versions

A CSV of failed pipeline runs answers nothing until someone reads it, and a summary pasted into chat is stale the moment the next failure lands. You will turn the CSV into a private page on `claude.ai`, revise that page in place so the same URL carries three versions, restyle it from design tokens kept in `CLAUDE.md`, and then deny the `Artifact` tool to see what Claude does when it cannot publish. You finish with a log that ties each version to the prompt that produced it.

What you practice here: publish session output as a page, update the same URL from a fresh session, steer its look from the repository, and recognise the fallback when publishing is blocked.

Duration: about 70 minutes.

Teaching for this lab lives in [Turn Session Output into a Shareable Page](../../../demos/01-fundamentals/06-artifacts/readme.md); the publish loop is walked through in [Publish, Revise and Share a Decision as an Artifact](../../../demos/01-fundamentals/06-artifacts/demo-artifact-publish-share.md). The design tokens in Step 5 follow [Make the Page Look Like Your Product](../../../demos/01-fundamentals/06-artifacts/readme.md#make-the-page-look-like-your-product), and the deny rule in Step 7 follows [Availability and Turning It Off](../../../demos/01-fundamentals/06-artifacts/readme.md#availability-and-turning-it-off). This lab needs Claude Code v2.1.183 or later and a session signed in with `/login` on a Pro, Max, Team or Enterprise plan.

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code or the shell
- **Expected result**: what the outcome looks like

You build four things in the starter folder: a page in `pages/`, a `## Design system` section in `CLAUDE.md`, a temporary deny rule in `.claude/settings.local.json`, and `ARTIFACT-LOG.md`. The page itself lives at a `claude.ai/code/artifact/...` URL that only you can open.

## Where to Open Claude Code

The starter holds `ci-failures.csv` with 22 failed runs over three weeks, `new-failures.csv` with three later rows, `check-totals.py` for cross-checking numbers, and a `CLAUDE.md` that describes the data. It has no pages and no design tokens yet. Run this from the repository root.

```bash
cd labs/01-fundamentals/07-publish-an-artifact/starter && claude
```

```powershell
cd labs/01-fundamentals/07-publish-an-artifact/starter; claude
```

Accept the trust dialog on the first start. The lab publishes to a private page: nothing in it is shared with anyone, and Step 8 lists what to clean up.

---

## Step 1: Confirm the Session Can Publish

**Goal:** Know before you build anything that the three conditions for publishing hold.

An artifact needs a recent client, a claude.ai sign-in and the Anthropic API as provider. A session that misses one of them quietly writes a local HTML file, which looks like success until you search for the URL. Check all three now.

```text
/status
```

**Prompt:**

```text
Tell me three things in one line each: the Claude Code version, which account or login method this session uses, and whether you have an Artifact tool available right now. Do not publish anything.
```

**Expected result:** the version is 2.1.183 or higher, the login method names a claude.ai account with no API key in use, and Claude states that it has an Artifact tool. If the version is lower, update Claude Code and restart. If the login is an API key or a cloud-provider credential, run `/login` with a claude.ai account and restart. Every later step depends on this answer.

---

## Step 2: Publish the CSV as a Page

**Goal:** Run the publish loop end to end and hold a URL.

Claude writes an HTML file to your project, asks permission once for this new artifact, prints a URL and opens it. The prompt below names the title, the output folder and the content, so nothing is left to chance. The inline SVG instruction matters: a page cannot load external scripts or fonts, so charts must live inside the file.

**Prompt:**

```text
Read ci-failures.csv and build a dashboard artifact titled "CI failures, three week view". Write the file to pages/ci-failures.html.

Include:
- failure count and lost minutes per service, as a bar chart
- a table of the five error strings that cost the most total minutes, with count and total minutes
- one short paragraph naming the single error that costs the most minutes, with the arithmetic shown

Use inline SVG for the chart and keep the page self-contained: no external scripts, fonts or images.
```

Then cross-check the numbers Claude put on the page against the script in the starter.

```bash
python check-totals.py
```

```powershell
python check-totals.py
```

**Expected result:** Claude asks permission with a prompt close to `Claude wants to publish "CI failures, three week view" (ci-failures.html) to a private page on claude.ai`. Approve it, and Claude prints a `claude.ai/code/artifact/...` URL while your browser opens the page. The script prints `checkout-api` first with 6 failures and 86 minutes and ends with `total` at 22 failures and 249 minutes; the chart on the page must match those values. The paragraph names `timeout waiting for payment-stub` at 62 minutes (14 + 16 + 15 + 17).

Copy the URL into a scratch note, because Step 4 needs it.

---

## Step 3: Revise the Same URL and Read the Versions

**Goal:** See that a revision lands on the same URL as a new version and asks for no second approval.

Every publish of an existing artifact becomes a version. The page header carries a Share control with a version picker, so you can later pin a reviewer to one version while the page moves on.

**Prompt:**

```text
Add a section below the chart to pages/ci-failures.html with failures per week per service, as a table with one row per service and one column per week starting on the Monday of each week. Under it add one line that compares the last week to the first week in total failures. Republish to the same artifact.
```

**Expected result:** no permission prompt appears, because the artifact was approved in Step 2, and Claude prints the same URL. Reload the page in the browser: the weekly table is there. Open the Share control in the page header and find the version picker; it lists two versions. The weekly table shows two week columns, for the weeks starting 2026-07-06 and 2026-07-13, because the data ends on 2026-07-17.

---

## Step 4: Update the Page From a Fresh Session

**Goal:** Learn that the URL is how a new session finds an existing artifact.

A different session knows nothing about your artifact. Give it the URL and it revises the page you already have; leave the URL out and you get a second artifact next to the first. You will do it the right way; the Expected result below shows what the wrong way produces.

Add the three later failures to the CSV from a second terminal in the starter folder, or from the same shell if you use the `!` prefix inside Claude Code.

```bash
cat new-failures.csv >> ci-failures.csv
python check-totals.py
```

```powershell
Get-Content new-failures.csv | Add-Content ci-failures.csv
python check-totals.py
```

Type `/exit`, start `claude` again in the starter folder, and paste the prompt with your own URL in place of the placeholder.

**Prompt:**

```text
Update the artifact at <paste your URL from Step 2> with the new rows in ci-failures.csv: refresh the chart, the top-five table, the paragraph and the weekly table, and republish it as a new version of that same artifact. Keep pages/ci-failures.html as the source file.
```

**Expected result:** the totals line of `check-totals.py` now reads 25 failures and 280 minutes, with `checkout-api` at 7 failures and 104 minutes. Claude republishes without a new permission prompt and prints the same URL. The page shows a third week column for the week starting 2026-07-20 and the share control lists three versions. If Claude printed a different URL, it created a second artifact: paste the original URL again and repeat the prompt.

The gallery at `claude.ai/code/artifacts` shows one artifact with this title and no second copy.

---

## Step 5: Restyle the Page From Design Tokens in CLAUDE.md

**Goal:** Steer the look of every future page from a file in the repository, with no styling words in the prompt.

Claude applies a built-in design skill that looks for a design system in the project first. The tokens go where Claude already reads: `CLAUDE.md`. Append this section to the starter's `CLAUDE.md`.

```markdown
## Design system

- Colors: primary #0b6e4f, accent #d9480f, surface #f4f7f5, text #14201b
- Typography: system sans-serif for body, ui-monospace for numbers and code
- Spacing: 8px scale, 4px border radius, no shadows
- Charts: bars use primary, the single most expensive item uses accent
```

Restart so the new section is loaded, then confirm Claude can see it.

```text
/memory
```

**Prompt:**

```text
Restyle pages/ci-failures.html to follow the Design system section of CLAUDE.md, without changing any numbers or text content, and republish it to the same artifact.
```

Then count the token values in the source file.

```bash
grep -o -i -E "#0b6e4f|#d9480f|#f4f7f5|#14201b" pages/ci-failures.html | sort | uniq -c
```

```powershell
Select-String -Path pages/ci-failures.html -Pattern '#0b6e4f|#d9480f|#f4f7f5|#14201b' -AllMatches | ForEach-Object { $_.Matches.Value.ToLower() } | Group-Object | Select-Object Count, Name
```

**Expected result:** the page reloads at the same URL with a green and orange palette, a light green-grey background, square-ish corners and no shadows. The most expensive bar, `checkout-api`, is orange and the other bars are green. The search finds all four hex values at least once; a missing value means Claude chose its own colour, so repeat the prompt and name the missing token. The four versions in the Share control now read as a history of the data and then the look, with the numbers unchanged.

---

## Step 6: Test the Precedence: Prompt Over Design System

**Goal:** Confirm that an explicit instruction in the prompt outranks the tokens in `CLAUDE.md`.

The order is prompt, then your design system, then Claude's own choices. You will override one token for a single publish and then check that the file on disk reflects it.

**Prompt:**

```text
For this one publish only, make the accent colour #1d4ed8, overriding the CLAUDE.md accent, then republish pages/ci-failures.html to the same artifact. Do not edit CLAUDE.md.
```

Check that the token file stayed as you wrote it and that the page changed.

```bash
grep -c "d9480f" CLAUDE.md
grep -o -i "#1d4ed8" pages/ci-failures.html | wc -l
```

```powershell
(Select-String -Path CLAUDE.md -Pattern 'd9480f').Count
(Select-String -Path pages/ci-failures.html -Pattern '#1d4ed8' -AllMatches).Matches.Count
```

**Expected result:** the most expensive bar on the live page is blue, `CLAUDE.md` still contains the orange token, and the first command prints `1` while the second prints a number above zero. The override lives in this publish only. Restore the look with the next prompt and confirm the bar is orange again.

```text
Republish pages/ci-failures.html to the same artifact using only the Design system section of CLAUDE.md, with no overrides.
```

---

## Step 7: Deny the Artifact Tool and Read the Fallback

**Goal:** See what happens when publishing is blocked, so you can recognise the symptom in a repository that never allows it.

A repository can switch artifacts off with a permission rule. Create `.claude/settings.local.json` in the starter folder (make the `.claude` folder first) with this content. The file stays local to your checkout.

```json
{
  "permissions": {
    "deny": ["Artifact"]
  }
}
```

Restart Claude Code in the starter folder, then open the permission list.

```text
/permissions
```

**Prompt:**

```text
Add a one-line "Top error this week" callout at the top of pages/ci-failures.html showing the error string with the most lost minutes in the newest week, and publish the update to the same artifact.
```

**Expected result:** `/permissions` lists a deny rule for `Artifact` attributed to `.claude/settings.local.json`. Claude edits `pages/ci-failures.html` on disk, because file edits are still allowed, and then reports that it cannot publish, or writes the file and offers no URL. No permission prompt for publishing appears, because a denied tool never asks. Reload the live page in the browser: it does not show the callout, so the published artifact is unchanged and the local file is ahead of it.

Open the local file in a browser to see the callout.

Now remove the rule by deleting the `deny` entry from `.claude/settings.local.json`, restart, and republish the pending change.

```text
Publish pages/ci-failures.html to the existing artifact so the live page matches the file.
```

The live page now shows the callout at the same URL, as a new version.

---

## Step 8: Audit the Page and Write the Log

**Goal:** Leave a record that ties every version to the prompt that produced it, and check the page against the single-page constraints.

An artifact is served under a strict content security policy, so a page that reaches for another host is broken for every viewer. Check the file for any such reference before you log it.

```bash
grep -n -i -E "src=\"http|href=\"http|@import|fetch\(" pages/ci-failures.html
```

```powershell
Select-String -Path pages/ci-failures.html -Pattern 'src="http','href="http','@import','fetch\('
```

**Expected result:** the search prints nothing, which means the page makes no external request. A match is a bug to fix: ask Claude to inline that resource and republish. The file size is also worth a look with `ls -l pages` or `Get-ChildItem pages`; a page of this kind is a few kilobytes, far below the 16 MiB limit.

**Prompt:**

```text
Create ARTIFACT-LOG.md in this folder with the heading "# Artifact log". Start with one line: the artifact URL. Then add a Markdown table with the columns Version | What changed | Prompt summary, one row per version of the artifact in the order I published them, from the first page to the final republish. After the table add three short bullets: the file the page is built from, where the design tokens live, and the rule file that denied publishing in Step 7. Use only what happened in this lab, and write "unknown" for anything you cannot tell.
```

Last, remove the deny rule file if it still exists, and decide about the artifact itself. The artifact is private to you, so leaving it costs nothing; delete it from the gallery at `claude.ai/code/artifacts` if you prefer a clean account.

**Expected result:** `ARTIFACT-LOG.md` holds the URL, a table with seven rows (first page, weekly table, new rows, restyle, accent override, restore, callout) and three bullets naming `pages/ci-failures.html`, `CLAUDE.md` and `.claude/settings.local.json`. Check the row count against the version list in the Share control; a row you cannot find there is an invented version, so remove it. Your deliverables are the live page, the `## Design system` section in `CLAUDE.md` and `ARTIFACT-LOG.md`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Claude writes an HTML file and prints no URL | The session is not signed in with claude.ai, the plan lacks artifacts, or an `Artifact` deny rule is active | Run `/status`, sign in with `/login`, and check `/permissions` for a deny rule |
| A second artifact appears in the gallery | The prompt carried no URL, or a different one | Paste the first artifact's URL into the prompt and republish; delete the stray copy from the gallery |
| The restyle ignores your colours | `CLAUDE.md` was edited after the session started | Run `/exit`, start `claude` again, check `/memory`, and repeat the prompt |
| The browser does not open on publish | `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0` is set in your shell | Open the printed URL by hand |
| `python` is not found on macOS or Linux | The interpreter is called `python3` | Use `python3` in every command |
