---
name: feedback-reindex-exit-code
description: The Elasticsearch reindex job fails silently past 100k records unless its exit code is alerted on
metadata:
  type: feedback
  modified: 2026-04-29T07:30:00.000Z
---

Treat the Elasticsearch reindex job as failed until its exit code has been checked.

**Why:** INC-003 ran for six hours because the reindex failed silently once the product catalog exceeded 100k records, and nothing alerted on the job's exit code.

**How to apply:** Any change to the reindex job keeps the exit-code monitor and the Slack alert on failure. The job runs at 02:00 UTC; a green dashboard without an exit-code check is not evidence it ran.
