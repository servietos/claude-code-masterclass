# In-Context Approach

**Architecture:** Load the full corpus into every prompt turn.

**Sample question:**

What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?

**Prompt:**

Below is the complete knowledge base for this project.

---

[contents of corpus/incidents.md]

[contents of corpus/decisions.md]

[contents of corpus/team-notes.md]

---

Question: What was the root cause of INC-001, and which ADR was adopted as a direct consequence of that incident?
