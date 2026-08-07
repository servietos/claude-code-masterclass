# Publish Your Last Two Emails as a Self-Refreshing Page

One prompt publishes a page that fetches your two most recent emails every time it is opened.

------

Setup is `cd demos/04-mcp/04-artifact-connectors` then `claude`, with `/login` done and the Microsoft 365 connector added under Settings > Connectors on claude.ai.

## Publish It

```text
Build an artifact page titled "My last two emails" that fetches my two most
recent emails live through my Microsoft 365 connector each time the page
loads, showing sender, subject, received time and a one-line summary of each,
plus a "Data as of" line filled from the time of the call.
```

Expected Outcome: an approval naming the connector the page may call, then a `claude.ai/code/artifact/...` URL. Refresh the page and the "Data as of" stamp moves. Open the Share control and no public link is offered, because the call runs as whoever is viewing. Ask for the same page from the local `workiq` server instead and the emails are baked in at publish time and never change.

