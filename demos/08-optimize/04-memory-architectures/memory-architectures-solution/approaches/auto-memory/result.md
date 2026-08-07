# Auto-Memory Result

INC-001 root cause: connection pool exhaustion in PaymentsService, max connections set to 5 against a peak of 40 concurrent checkout requests. Fixed by raising the pool to 50 and adding a 10s circuit breaker.

ADR-001 (event sourcing for order state) was adopted as a direct consequence, which the memory file states outright.

The index alone would not have answered this: it names the incident and the ADR link, but the pool numbers live in the file body that the matching index line pointed at.
