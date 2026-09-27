# .NET Testing Patterns

Reference for xUnit, FluentAssertions, and NSubstitute. Target 80%+ behavior-focused coverage.

Open the one sub-leaf that matches the symptom or task.

| You want to... | Read |
|---|---|
| Lay out a test class, mock the DbContext, know how much to cover | [writing-tests](dotnet-testing-writing-tests.md) |
| Look up `[Theory]`, `BeEquivalentTo`, `Substitute.For`, `Received`, `Arg.Is` | [library-syntax](dotnet-testing-library-syntax.md) |
| Fix a red suite: real assertion message, which side is wrong, delegation | [failing-suite](dotnet-testing-failing-suite.md) |
| Know why tests pass but the running API fails (in-memory, timezone, `date`) | [environment-gaps](dotnet-testing-environment-gaps.md) |
| Stop `WebApplicationFactory` authenticating every request | [auth-factory](dotnet-testing-auth-factory.md) |
| Build while a dev instance holds `bin/` (MSB3021/MSB3027, `No data found`) | [locked-bin](dotnet-testing-locked-bin.md) |
| Fix an endpoint returning `Success = true` for a lookup that matched nothing | [false-success-endpoint](dotnet-testing-false-success-endpoint.md) |
| Know what runtime evidence you still owe after a green unit test | [runtime-receipts](dotnet-testing-runtime-receipts.md) |

**Never weaken an assertion to reach green.**
