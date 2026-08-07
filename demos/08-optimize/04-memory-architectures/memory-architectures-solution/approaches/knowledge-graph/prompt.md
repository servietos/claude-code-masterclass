# Knowledge Graph Approach

**Architecture:** Retrieve relevant subgraph by entity query; load only matching nodes and relations.

**Query:** INC-001, ADR-001

**Retrieved subgraph:**

Entities: INC-001, ADR-001, PaymentsService
Relations: INC-001 triggered ADR-001; INC-001 root_cause PaymentsService (pool exhaustion: max 5, peak 40 concurrent)

**Prompt:**

Using the retrieved graph context:
- INC-001 triggered ADR-001
- INC-001 root_cause: PaymentsService, pool exhaustion: max 5, peak 40 concurrent

Question: What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?
