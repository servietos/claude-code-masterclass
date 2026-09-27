# Writing [Description] text so the model picks the right tool

## Writing Tool Descriptions for LLM Disambiguation

Once a server has more than a couple of tools that touch related data (e.g. an aggregate total, a per-entity breakdown, and a derived/net figure), a client LLM will regularly pick the wrong one unless each `[Description]` earns its keep. A description that only states what the tool does is not enough once a near-neighbor tool exists — it must also say what it is *not*, so the model can rule out the alternative on the same pass:

- **State the disambiguation explicitly, by tool name.** "Returns the single aggregate total (not per-customer) — for a per-entity breakdown use `GetXByCategory` instead" beats two descriptions that both independently say "returns totals" and leave the model to guess which one is the aggregate.
- **Include the natural user question verbatim**, not just the technical operation. Users ask "how much was my revenue in 2022," not "aggregate income query" — echo the former in the description so embedding/keyword matching on the tool list actually surfaces it.
- **Name domain near-synonyms that map to different fields.** Many business domains have two or more terms that sound interchangeable to a general model but are computed differently server-side (e.g. gross turnover vs. net income; a domain's internal jargon vs. the everyday word a user would type, possibly in a different language than the codebase). If the underlying query already returns both, say so explicitly (`GrossX is the turnover figure, NetX is the income figure`) instead of leaving the model to infer which field answers which phrasing.
- **Verify the semantic claim against the query/service implementation before writing it** — don't guess which field maps to which business term; open the underlying `*Query`/`*Service` method and confirm what it actually aggregates. A confidently wrong disambiguation is worse than a vague one.
- **Prefer fixing descriptions over adding a new tool.** A new tool is only justified when the underlying data genuinely isn't computable from an existing tool's return shape — if two "different" questions already resolve to the same query with different wording, that's a description gap, not a coverage gap.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)
