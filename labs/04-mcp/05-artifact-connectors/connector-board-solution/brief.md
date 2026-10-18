# Issue Pulse Board Brief

Audience: the maintainers of a public repository who want one page that always shows what changed last.

## Source

- Repository: `anthropics/claude-code` on GitHub (public, so any GitHub connector account can read it)
- Records: the 10 most recently updated open issues
- Access: through the viewer's own claude.ai GitHub connector at view time

## Fields per record

| Field | Meaning |
|-------|---------|
| Number | Issue number, linked to the issue |
| Title | Issue title |
| Author | Login of the reporter |
| Labels | Label names, comma separated |
| Updated | Time of the last update, shown as a relative age |

## Sections

| Section | Content |
|---------|---------|
| Header | Page title and a "Data as of" line filled from the time of the connector call |
| Latest issues | The 10 records above, newest update first |
| Label counts | How many of those 10 records carry each label |

## Quality bar

- The records are never typed into the page; every number, title and label arrives from the connector call.
- Each live section says what it needs when the connector is missing.
- The page is readable at phone width.
