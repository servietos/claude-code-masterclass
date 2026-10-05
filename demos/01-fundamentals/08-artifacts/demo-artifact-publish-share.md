# Publish, Revise and Share a Decision as an Artifact

An artifact turns a result into a private hosted page a colleague can open, updated in place at the same URL. You take three weeks of CI failures from a CSV, publish them as a page, revise it, make it follow design tokens stored in `CLAUDE.md`, then use it to lay out three remediation options and hand the chosen one back to the session as a prompt. You finish knowing which decisions belong on a page, what the strict Content Security Policy does to one, and how to turn publishing off for a repository that should never send anything outward.

---

## Prerequisites

Artifacts publish only from a session signed in to a claude.ai account on a Pro, Max, Team, or Enterprise plan, running against the Anthropic API on Claude Code v2.1.183 or later. Run `/login` before you start. If your session uses an API key, a gateway token, or Bedrock, Vertex, or Foundry credentials, Claude will write a local HTML file and print no link: open that file in a browser and follow the rest of the demo from disk, skipping the sharing steps.

Start in the sandbox folder:

```bash
cd demos/01-fundamentals/08-artifacts/artifact-sandbox
claude
```

## Demo Files

The sandbox holds one file, and every page you publish is built from it. Everything else in this demo is generated during the run and removed at the end.

| File | What it represents |
|------|--------------------|
| `deploy-failures.csv` | Three weeks of CI failures across five services, with stage, error, duration, and what triggered the run |

---

## Step 1: Decide What Belongs on a Page

Overview: Publishing is not free. A page costs more output tokens than the same answer as text, it lands somewhere outside your terminal, and a page nobody opens is worse than three lines of output. The judgement worth building first is which results are genuinely easier to look at than to read.

Research / Planning / Discussion:

```text
Read deploy-failures.csv in this folder.

I could answer questions about this data three ways: as terminal text, as a
file I open in an editor, or as a published artifact page.

For each of the five questions below, tell me which of the three fits and why:

1. Which service failed most often?
2. How do failure counts break down by service and by stage over time?
3. Which single failure should we fix first?
4. What would three different remediation plans look like side by side?
5. What is the median failure duration?

Do not build anything yet.
```

Finding: A useful answer sends questions 1 and 5 to terminal text, since a single number gains nothing from a layout, and sends 2 and 4 to a page, because comparison across two dimensions and comparison across alternatives are exactly what a page does better than prose. Question 3 is the interesting one: the recommendation is defensible either way, and the reasoning it gives you is what matters. Push back if every question comes back as an artifact, which is the tell that the model is treating the feature as a default rather than a choice.

Expected Outcome: a five-row answer in the terminal with a medium named for each question and a reason attached. Nothing is published yet, and no file has been written.

---

## Step 2: Publish the First Page

Overview: This step runs the publish loop end to end: Claude writes a file, asks for permission once, prints a URL, and opens it. Watching the permission prompt matters, because it names the exact file about to leave your machine.

Research / Planning / Discussion:

```text
Before you publish anything, tell me what a Claude Code artifact actually is
in mechanical terms.

1. What gets written to my project, and in what file formats?
2. Where does the published page live, and who can see it by default?
3. What does the page get wrapped in, and what does that stop it from doing?

Two or three sentences each.
```

Finding: Expect an `.html`, `.htm`, or `.md` file written into your project, a private URL on claude.ai visible only to you until you share it, and an HTML shell served under a strict Content Security Policy that blocks every external request. If the answer suggests the page can call your API or store what a viewer types, correct it now: the page has no backend, and believing otherwise leads to asking for pages that cannot work.

Recipe:

```text
Read deploy-failures.csv and build a dashboard artifact from it titled
"CI failures, three week view".

Include:
- failure counts by service, as a bar chart
- a heatmap or grid of service against stage
- a table of the five most repeated error strings with their counts
- one short paragraph naming the single failure pattern that costs the most
  total minutes, with the arithmetic shown

Use inline SVG for the charts rather than embedded images, and keep the whole
page self-contained.
```

Expected Outcome: a permission prompt naming the title and the file, worded close to `Claude wants to publish "CI failures, three week view" (ci-failures.html) to a private page on claude.ai`. Approve it and Claude prints a `claude.ai/code/artifact/...` URL and your browser opens the page. Confirm two things: the HTML file now exists in the sandbox folder, and the timeout in `checkout-api` integration tests is identified as the most expensive pattern. Press `Ctrl+]` in the terminal to reopen the page without hunting for the URL.

---

## Step 3: Revise in Place and Control What Reviewers See

Overview: An artifact is not a one-shot export. Republishing goes to the same URL, every publish becomes a version, and the page updates under anyone who has it open. This is what makes it usable during a long task rather than only at the end.

Research / Planning / Discussion:

```text
I have an artifact published. Explain the versioning and sharing model:

1. What happens to the URL when you republish?
2. What does a person with the page already open see at that moment?
3. If I send this link to a reviewer today and keep revising tomorrow, what do
   they see, and what control do I have over that?
4. What happens if I open a brand new session and ask you to update it?
```

Finding: The answer should keep the URL stable across republishes, update open pages live, and describe the Share control's version picker and its always-share-latest option as the lever for question 3. Question 4 is the one that catches people: a new session with no URL creates a second artifact instead of a new version, so the URL has to be pasted in. If the response claims a new session can find the artifact by name, that is wrong.

Recipe:

```text
Add a per-week breakdown below the existing charts, showing failures per week
per service, and add a short "what changed" line under it comparing the last
week to the first. Republish to the same artifact.
```

Expected Outcome: the same URL, now showing the weekly section, with no second permission prompt because the artifact was already approved. Open the Share control in the page header and confirm you see the version picker with more than one version listed, the always-share-latest toggle, and an audience selector whose options depend on your plan. Do not share it yet.

---

## Step 4: Make Every Page Look Like Your Product

Overview: Claude styles artifacts with a built-in design skill, which is why the first page already looked deliberate. That skill checks your project for an existing design system before choosing its own, so a short block in `CLAUDE.md` changes every artifact this project ever publishes. This is the same mechanism the constitution topic teaches, applied to visual output.

Research / Planning / Discussion:

```text
When you build an artifact for this project, where do you look for colors,
typography, and spacing before deciding on your own?

Rank these three sources by precedence and say what happens when they
disagree: the instruction in my prompt, a design system recorded in
CLAUDE.md, your own default choices.
```

Finding: The order is prompt first, project design system second, built-in defaults last. A good answer also says the design system can live anywhere Claude reads, `CLAUDE.md` or a theme file, and that it is prose rather than a schema. If the response asks you for a config file format, it has invented a requirement.

Recipe: create `CLAUDE.md` in the sandbox folder with this content, then republish.

```markdown
# CI failure review

## Design system

- Colors: primary #1a4d8f, accent #f59e0b, surface #f8fafc, danger #b91c1c
- Typography: Inter for body, JetBrains Mono for code and numeric tables
- Spacing: 8px scale, 6px border radius
```

```text
Republish the CI failures artifact using this project's design system.
```

Expected Outcome: the same URL, restyled. Charts and headings now use the primary and accent colors from the block, numeric columns render in a monospace face, and the danger color appears on the worst-performing rows. If nothing changed, confirm the file is named `CLAUDE.md` in the folder you started the session from, and check `/memory` to see whether it was loaded.

---

## Step 5: Draft Alternatives, Then Bring the Decision Back

Overview: Comparison is the pattern artifacts are best at, and it is the one that changes how you work. Instead of arguing about three plans in prose, you put them next to each other and pick one. The step closes the loop by having the page emit a prompt you paste back into the session, so the decision becomes work rather than a page nobody acts on.

Research / Planning / Discussion:

```text
Based on the CI failure data you already analysed, draft three genuinely
different remediation plans for the most expensive failure pattern.

Make them differ in approach, not in wording: one that treats the symptom, one
that changes the test architecture, and one that removes the dependency
entirely. For each, state the effort, the risk, and what it does not fix.

Do not build a page yet.
```

Finding: Three plans that differ only in how aggressively they retry are one plan in three costumes, and that is the failure mode to push back on. Look for a real spread: a longer timeout, a contract-test replacement for the payment stub, and a plan that removes the stub from the integration path. Each should name what it leaves unsolved, because that is the column you will compare against.

Recipe:

```text
Build a decision artifact from those three plans, published as a new artifact
titled "Checkout-api timeout: three plans".

Lay them out as three columns with the same rows in each: approach, effort,
risk, what it does not fix, and a one-line recommendation. Highlight the plan
you recommend and say why in one sentence.

Add a "Copy as prompt" button under each column that copies a complete,
self-contained implementation prompt for that plan to the clipboard, written
so I can paste it straight into a new Claude Code session.
```

Expected Outcome: a second artifact at its own URL, with a fresh permission prompt because it is a new artifact rather than a new version. Three columns render side by side, and the button under your chosen column copies a prompt that names the file, the change, and the verification step. Paste it back into your session and confirm it reads as a complete instruction with no reference to the page it came from. Share this one from the page header, using the audience your plan offers.

---

## Step 6: Find the Edges and the Off Switch

Overview: Two things are worth learning deliberately rather than discovering during a demo to someone else: what the Content Security Policy refuses to do, and how to stop a repository from publishing at all. Both are one command away.

Research / Planning / Discussion:

```text
I want to add an interactive chart to the artifact using a charting library
from a CDN, and have the page fetch fresh CI data from our internal API each
time someone opens it.

Tell me which parts of that are impossible in an artifact and why, and what
you would do instead for each. Be specific about the mechanism that blocks it.
```

Finding: Both requests are blocked by the same Content Security Policy: no script from another host, and no `fetch`, XHR, or WebSocket to anything. The substitutes are inlining the library or hand-rolling the chart as SVG, and baking the data into the page at publish time. A complete answer names MCP connectors as the single exception for live data, which is the subject of the MCP module rather than this one. If the response offers a proxy or a workaround, it has missed that the policy is enforced by the viewer, not by Claude.

Recipe: deny the tool for this folder, then prove it took effect.

```json
{
  "permissions": {
    "deny": ["Artifact"]
  }
}
```

Save that as `.claude/settings.json` inside the sandbox folder, restart the session, then ask for a page again:

```text
Rebuild the CI failures dashboard as a page.
```

Expected Outcome: Claude writes the HTML file to disk and tells you it cannot publish, with no URL and no permission prompt. Open the file directly in a browser and confirm it renders standalone, which is the same fallback an API-key session gets. This is the state to recognise when artifacts appear to be missing: the tool is denied or unavailable, not broken.

