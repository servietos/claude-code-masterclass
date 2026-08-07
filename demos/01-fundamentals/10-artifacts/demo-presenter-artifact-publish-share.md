---
presents: demo-artifact-publish-share.md
budget: 5 min
beats: 5
---

# Present: Publish, Revise and Share a Decision as an Artifact

Five beats take a CSV to a published page, restyle it from project design tokens, and then switch publishing off. The room walks away able to say which results are worth a page, what the Content Security Policy refuses to do, and how to stop a repository from publishing at all.

------

**No solution folder ships.** The sandbox holds one tracked file, `deploy-failures.csv`, and every page in the demo is built from it; the run's other artifacts are two URLs in the presenter's own gallery.

## Beats

### Beat 1: Most results do not belong on a page (1 min)

**Open:** [`artifact-sandbox/deploy-failures.csv`](artifact-sandbox/deploy-failures.csv) · [Step 1: Decide What Belongs on a Page](demo-artifact-publish-share.md#step-1-decide-what-belongs-on-a-page)
**Say:** Publishing costs tokens and attention, and a page nobody opens is worse than three lines in the terminal. What a page does better than prose is comparison.

```text
Read deploy-failures.csv in this folder.

I could answer questions about this data three ways: as terminal text, as a
file I open in an editor, or as a published artifact page.

For each of the five questions below, tell me which of the three fits and why:

...

Do not build anything yet.
```

**Result:** nothing published and no file written; two of the five earn a page, questions 2 and 4, while 1 and 5 are single numbers and 3 is defensible either way.

**Gotcha:** if all five come back as artifacts, the model is treating the feature as a default rather than a choice.

### Beat 2: The publish loop, and the prompt that names the file (1 min)

**Open:** [Step 2: Publish the First Page](demo-artifact-publish-share.md#step-2-publish-the-first-page) · [`readme.md`](readme.md#publish-one)
**Say:** An artifact is published from a real file in your project, which is what makes the loop inspectable. Approval is asked once per artifact, so the first one is the one to read properly.

```text
Read deploy-failures.csv and build a dashboard artifact from it titled
"CI failures, three week view".

Include:
- failure counts by service, as a bar chart
...

Use inline SVG for the charts rather than embedded images, and keep the whole
page self-contained.
```

**Result:** `ci-failures.html` lands in [`artifact-sandbox/`](artifact-sandbox/) beside the CSV, a `claude.ai/code/artifact/...` URL is printed, and the approval names the file about to leave the machine

```text
Claude wants to publish "CI failures, three week view" (ci-failures.html) to a private page on claude.ai
```

**Gotcha:** `Ctrl+]` reopens the page later without hunting for the link.

### Beat 3: One URL, many versions, and a second session that does not know about it (1 min)

**Open:** [Step 3: Revise in Place and Control What Reviewers See](demo-artifact-publish-share.md#step-3-revise-in-place-and-control-what-reviewers-see) · [`readme.md`](readme.md#update-it-and-choose-what-viewers-see)
**Say:** A stable address with versions behind it is what separates an artifact from an export. A page's identity lives in its URL and nowhere else.

```text
I have an artifact published. Explain the versioning and sharing model:

1. What happens to the URL when you republish?
2. What does a person with the page already open see at that moment?
3. If I send this link to a reviewer today and keep revising tomorrow, what do
   they see, and what control do I have over that?
4. What happens if I open a brand new session and ask you to update it?
```

**Result:** nothing new on disk and no second permission prompt; the second version exists only at the Beat 2 URL, whose Share control now lists more than one version.

**Gotcha:** question 4 is the trip-up: a new session with no URL creates a second artifact instead of a new version.

### Beat 4: Three lines in CLAUDE.md restyle every page the project publishes (1 min)

**Open:** [Step 4: Make Every Page Look Like Your Product](demo-artifact-publish-share.md#step-4-make-every-page-look-like-your-product) · [`readme.md`](readme.md#make-the-page-look-like-your-product)
**Say:** Pages arrive already styled, so a palette is chosen for you on every publish unless the project states one of its own. This is the constitution mechanism applied to visual output.

```markdown
# CI failure review

## Design system

- Colors: primary #1a4d8f, accent #f59e0b, surface #f8fafc, danger #b91c1c
- Typography: Inter for body, JetBrains Mono for code and numeric tables
- Spacing: 8px scale, 6px border radius
```

**Result:** `CLAUDE.md`, written by this step into [`artifact-sandbox/`](artifact-sandbox/), is the whole styling input; the same URL comes back with the primary and accent colours on the charts and the danger colour on the worst rows.

**Gotcha:** it is prose rather than a schema, so any clear list of colours, fonts and spacing works: asking for a config file format invents a requirement.

### Beat 5: The policy is the edge, the deny rule is the off switch (1 min)

**Open:** [Step 6: Find the Edges and the Off Switch](demo-artifact-publish-share.md#step-6-find-the-edges-and-the-off-switch) · [`readme.md`](readme.md#page-constraints) · [`readme.md`](readme.md#availability-and-turning-it-off)
**Say:** A CDN script and a live `fetch` are refused by one policy, enforced by the viewer rather than by Claude. A repository whose output must never leave the building needs publishing to be impossible, not discouraged.

```json
{
  "permissions": {
    "deny": ["Artifact"]
  }
}
```

**Result:** with `.claude/settings.json` saved, the HTML is written to disk and no URL is printed, the same fallback an API-key session gets

```diff
 artifact-sandbox/
   deploy-failures.csv
+  ci-failures.html
+  CLAUDE.md
+  .claude/settings.json
```

**Gotcha:** both refusals, a script from another host and a `fetch` to anything, come from the same policy: inline the library or hand-roll SVG, and bake the data in.

## If the room asks

| Question | Answer |
|---|---|
| Who can see a page I publish? | Only you until you share it; Pro and Max offer a public link, Team and Enterprise can grant named people or the whole organization. |
| I am on an API key or Bedrock. What happens? | Claude writes a local HTML file and prints no link; open it in a browser and skip the sharing steps. |
| What does a page cost compared to text? | More output tokens than the same content in the terminal, with data-URI images dominating; prefer SVG and summarize large data. |
| How do I stop a repository publishing anything? | Deny the `Artifact` tool, or set `disableArtifact` in settings, or export `CLAUDE_CODE_DISABLE_ARTIFACT=1` for one shell. |
| Only the CSV is tracked. What outlives the demo? | The two published pages. A shared link stays reachable from `claude.ai/code/artifacts` until it is deleted there. |
