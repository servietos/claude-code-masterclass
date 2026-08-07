---
name: feedback-auth-ttl-pairing
description: Never change the auth token TTL without changing the Redis session TTL to match
metadata:
  type: feedback
  modified: 2026-04-05T10:15:00.000Z
---

Never change AUTH_TOKEN_TTL_HOURS without changing the Redis session TTL to match.

**Why:** INC-002 was a P2 for two hours because JWT expiry was 1 hour in staging and 24 hours in prod, introduced in PR #412 during the environment consolidation. ADR-002 then bound the Redis TTL to the same value, so the two now drift together or not at all.

**How to apply:** When touching either TTL, change both in the same commit and state the new value in the PR description.
