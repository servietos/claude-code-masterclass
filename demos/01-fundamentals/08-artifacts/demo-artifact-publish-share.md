# Publish, Revise and Share a Decision as an Artifact

An artifact turns a result into a private hosted page a colleague can open, updated in place at the same URL. You take CI failures from a CSV, publish them as a page, revise it, then use it to lay out three remediation options and hand the chosen one back to the session as a prompt.

---

Work in `demos/01-fundamentals/08-artifacts/artifact-sandbox`, which holds `deploy-failures.csv`; no solution folder ships, so each page lands as an HTML file in that folder and at its own claude.ai URL.

## Step 1: Publish the First Page

This step runs the publish loop end to end: Claude writes a file, asks for permission once, prints a URL, and opens it. Run `/login` first, because artifacts publish only from a session signed in to a claude.ai account on a Pro, Max, Team, or Enterprise plan.

```text
Read deploy-failures.csv and build a dashboard artifact from it titled
"CI failures, three week view".

Include:
- failure counts by service, as a bar chart
- a heatmap or grid of service against stage
- a table of the five most repeated error strings with their counts
- one short paragraph naming the single failure pattern that costs the most
  total minutes, with the arithmetic shown

Use inline SVG for the charts, and keep the whole
page self-contained.
```

Expected Outcome: a permission prompt naming the title and the file, worded close to `Claude wants to publish "CI failures, three week view" (ci-failures-dashboard.html) to a private page on claude.ai`, where the file name is whatever the run picks.

Approve it and Claude prints a `claude.ai/code/artifact/...` URL and your browser opens the page. The HTML file now exists in the sandbox folder, and the timeout in `checkout-api` integration tests is identified as the most expensive pattern.

## Step 2: Revise in Place and Control What Reviewers See

Republishing goes to the same URL, every publish becomes a version, and the page updates under anyone who has it open.

```text
Add a per-week breakdown below the existing charts, showing failures per week
per service, and add a short "what changed" line under it comparing the last
week to the first. Republish to the same artifact.
```

Expected Outcome: the same URL, now showing the weekly section, with no second permission prompt because the artifact was already approved. The Share control in the page header lists more than one version in its version picker, with an always-share-latest toggle and an audience selector whose options depend on your plan.

A new session with no URL creates a second artifact, so paste the URL in when you update the page from a fresh session.

## Step 3: Draft Alternatives, Then Bring the Decision Back

Comparison is the pattern artifacts are best at: put three plans next to each other, pick one, and have the page emit a prompt you paste back into the session.

```text
Based on the CI failure data you already analysed, draft three genuinely
different remediation plans for the most expensive failure pattern.

Make them differ in approach: one that treats the symptom, one
that changes the test architecture, and one that removes the dependency
entirely. For each, state the effort, the risk, and what it does not fix.

Do not build a page yet.
```

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

Expected Outcome: a second artifact at its own URL, with a fresh permission prompt because it is a new artifact. The button under your chosen column copies a prompt that names the file, the change, and the verification step; paste it back into your session and confirm it reads as a complete instruction with no reference to the page it came from. Share this one from the page header, using the audience your plan offers.
