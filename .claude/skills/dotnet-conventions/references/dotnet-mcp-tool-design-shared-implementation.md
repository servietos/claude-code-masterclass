# A tool mirroring an endpoint shares its implementation and its guards

## A tool that mirrors an endpoint shares its implementation, never its rules

When a tool exposes something a controller already does, the validation usually lives inline in the
action method, so the quick path is to restate it in the tool. That produces two copies of the same
rules with no compiler link between them, and they drift on the first change that touches only one.

Extract the logic to the service the tool and the controller both call (validation included), then
make the controller delegate to it. The refactor is behaviour-preserving, so the existing controller
tests are the proof: they must pass untouched.

The same applies to guards. A tool wrapping a state-changing endpoint gets exactly the guards that
endpoint has, no fewer. Adding extra confirmation steps in the tool is a product decision, not a
default: raise it rather than inventing it, and remember the tool surface is reachable by any
connected client, so "the UI asks first" is not a guard.

Where a subset of tools is deliberately withheld from another consumer (an in-app assistant getting
reads but not writes), make the split explicit in code so a newly added tool must choose a side.
A default that silently includes new tools hands out write access nobody reviewed.

Back to the index: [dotnet-mcp-tool-design](dotnet-mcp-tool-design.md)
