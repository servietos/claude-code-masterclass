# Auto-Memory Approach

**Architecture:** a lean `MEMORY.md` index loads on every turn; the typed memory files it points at are read only when an index line looks relevant to the question.

**Index line that matched:** `[INC-001 pool exhaustion](project-inc-001-pool-exhaustion.md)`

**Files read:** `MEMORY.md`, `project-inc-001-pool-exhaustion.md`

**Prompt:**

[contents of MEMORY.md]

[contents of project-inc-001-pool-exhaustion.md]

Question: What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?
