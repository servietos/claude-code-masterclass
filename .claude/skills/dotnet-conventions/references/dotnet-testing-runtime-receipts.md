# A Green Test Is Not a Deployment Receipt

## A passing unit test is not a receipt for what a running system does

A fix reported "done" on a passing unit test asserting the calculation, plus reasoning that the
change was config-only, can still be unverified: the test was correct, the config was correct and
present, and the process actually answering the request was a stale build the fix never reached. The
unit test proves a pure function computes correctly in isolation. It says nothing about which process
is deployed, wired, or listening behind the port the caller actually hits.

When a fix is meant to change what a running system records or returns, hold it to a receipt the
test did not produce: the value in the live response, the row in the database, or the service's own
log line for that operation. Three independent sources agreeing is the bar, not a green `dotnet
test`.

Back to the index: [dotnet-testing](dotnet-testing.md)
