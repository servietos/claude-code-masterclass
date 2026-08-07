---
presents: demo-last-two-emails.md
budget: 2 min
beats: 1
---

# Present: Publish Your Last Two Emails as a Self-Refreshing Page

One prompt publishes a page that fetches the presenter's two most recent emails on every open.

------

### Beat 1: The page fetches as whoever is looking (2 min)

**Open:** [Publish It](demo-last-two-emails.md#publish-it) · [`readme.md`](readme.md#the-call-runs-as-the-viewer-not-as-you)
**Say:** A published page has no path back to your machine, so a local `.mcp.json` server can only bake data in; an account connector is called by claude.ai at view time.

```text
Build an artifact page titled "My last two emails" that fetches my two most
recent emails live through my Microsoft 365 connector each time the page
loads, showing sender, subject, received time and a one-line summary of each,
plus a "Data as of" line filled from the time of the call.
```

**Result:** an approval naming the connector, a URL, a "Data as of" stamp that moves on refresh, and a Share control with no public link.

**Gotcha:** hand the link to someone in the room and they see their own inbox, not yours.
