# Statefile Result

INC-001 root cause: PaymentsService connection pool exhaustion (max 5, peak load needed 40). Fixed by increasing pool to 50.

ADR-001 (event sourcing for orders) was adopted as a direct consequence: the STATE.md notes "Triggered by INC-001."
