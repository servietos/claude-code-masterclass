# In-Context Result

INC-001 was caused by connection pool exhaustion in PaymentsService (max 5 connections, 40 concurrent requests at peak). The fix increased the pool to 50 and added a circuit breaker.

ADR-001 (event sourcing for order state) was adopted as a direct consequence: the incident made replay requirements obvious, and event sourcing was chosen over mutable DB records specifically to handle that need.
