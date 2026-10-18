---
presents: demo-artifact-publish-share.md
budget: 4 min
beats: 2
---

# Present: Publish, Revise and Share a Decision as an Artifact

Two beats take a CSV to a published page and revise it in place at the same URL.

------

**No solution folder ships.** The sandbox holds one tracked file, `deploy-failures.csv`, and every page in the demo is built from it; the run's other artifacts are two URLs in the presenter's own gallery.

## Beats

### Beat 1: The publish loop, and the prompt that names the file (2 min)

**Open:** [Step 1: Publish the First Page](demo-artifact-publish-share.md#step-1-publish-the-first-page) · [`readme.md`](readme.md#publish-one)
**Say:** An artifact is published from a real file in your project, which is what makes the loop inspectable. Approval is asked once per artifact, so the first one is the one to read properly.

```text
Read deploy-failures.csv and build a dashboard artifact from it titled
"CI failures, three week view".

Include:
- failure counts by service, as a bar chart
...

Use inline SVG for the charts, and keep the whole
page self-contained.
```

**Result:** an `.html` page (`ci-failures-dashboard.html` in the verified run) lands in [`artifact-sandbox/`](artifact-sandbox) beside the CSV, a `claude.ai/code/artifact/...` URL is printed, and the approval names the file about to leave the machine

```text
Claude wants to publish "CI failures, three week view" (ci-failures-dashboard.html) to a private page on claude.ai
```

**Gotcha:** `Ctrl+]` reopens the page later without hunting for the link.

### Beat 2: One URL, many versions, and a second session that does not know about it (2 min)

**Open:** [Step 2: Revise in Place and Control What Reviewers See](demo-artifact-publish-share.md#step-2-revise-in-place-and-control-what-reviewers-see) · [`readme.md`](readme.md#update-it-and-choose-what-viewers-see)
**Say:** A stable address with versions behind it is what separates an artifact from an export. A page's identity lives in its URL and nowhere else.

```text
I have an artifact published. Explain the versioning and sharing model:

1. What happens to the URL when you republish?
2. What does a person with the page already open see at that moment?
3. If I send this link to a reviewer today and keep revising tomorrow, what do
   they see, and what control do I have over that?
4. What happens if I open a brand new session and ask you to update it?
```

**Result:** a written answer with no file changes: the URL stays the same on republish, the Share control lists each version, and a new session without the URL creates a second artifact at its own URL.

**Gotcha:** question 4 is the trip-up: a new session with no URL creates a second artifact at its own URL.

## If the room asks

| Question | Answer |
|---|---|
| Who can see a page I publish? | Only you until you share it; Pro and Max offer a public link, Team and Enterprise can grant named people or the whole organization. |
| I am on an API key or Bedrock. What happens? | Claude writes a local HTML file and prints no link; open it in a browser and skip the sharing steps. |
| Only the CSV is tracked. What outlives the demo? | The two published pages. A shared link stays reachable from `claude.ai/code/artifacts` until it is deleted there. |
