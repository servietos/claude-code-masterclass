# Unit-test your agent's performance

A sub-agent in `.claude/agents/` is a function: given a task prompt, it produces an output. Like any function, it can be wrong. The agent might miss cases, produce malformed output, ignore scope constraints, or hallucinate results it cannot verify. The only way to know is to run it against controlled scenarios and compare what it returns to what you expected.

Unit-testing an agent means defining a set of test cases, each with a concrete input prompt and a precise expected output, then running the agent in isolation and asserting the result. Each test targets one slice of the agent's behavior.

The agent under test in this topic is the `catalog-test-agent` you define in [Unit Test with a Permission-Locked Agent](../04-qa-agent/demo-test-food-controller.md). The code under test is `FoodController.cs` in that topic's own starter, `../04-qa-agent/catalog-service-cs`, which exposes five public action methods.

## Defining a Test Case

A test case has three parts: a prompt that represents one real task the agent should handle, the expected output the agent should return, and the assertion that determines pass or fail.

```text
Test: catalog-test-agent (happy path, all methods covered)

Prompt:
  You are catalog-test-agent. Read all public methods in
  ../04-qa-agent/catalog-service-cs/Controllers/FoodController.cs.
  Write xUnit tests covering each method with at least one happy-path and one
  edge-case test. Run dotnet test. Report results.

Expected:
  {
    "status": "pass",
    "testsPassed": 10,
    "testsFailed": 0,
    "errors": [],
    "summary": "10 tests written and passing for FoodController"
  }

Assert:
  - status is "pass"
  - testsPassed >= number of public methods * 2
  - testsFailed is 0
  - errors is empty
```

The expected output is a contract, not a script. The exact count depends on how the agent slices edge cases, so a higher number and different `summary` wording still pass; missing fields, a count below what the assertion demands, or a wrong status are failures.

## Designing Edge Case Tests

Happy-path tests confirm the agent works under ideal conditions. Edge cases reveal how it behaves when conditions are unusual. This case needs a file with no testable surface, and no such file ships with the starter: you write `../04-qa-agent/catalog-service-cs/Shared/EmptyService.cs` yourself, containing a constructor and private helpers only, then delete it once the test case has run so the starter stays pristine.

```text
Test: catalog-test-agent (no testable methods)

Prompt:
  You are catalog-test-agent. Read all public methods in
  ../04-qa-agent/catalog-service-cs/Shared/EmptyService.cs.
  The file contains only private methods and a constructor. Write tests.
  Run dotnet test. Report results.

Expected:
  {
    "status": "pass",
    "testsPassed": 0,
    "testsFailed": 0,
    "errors": [],
    "summary": "No public methods found; no tests written"
  }

Assert:
  - status is "pass"
  - summary acknowledges no public methods were found
  - agent does not hallucinate tests for private methods
```

The risk here is the agent writing tests for private or constructor code rather than reporting that no testable surface exists. A test that exposes this failure leads directly to a body instruction fix: "Do not write tests for private methods or constructors."

## Running the Test Suite

Run each test case by spawning the agent directly with its test prompt, then evaluate the returned JSON against your assertions.

```text
You are a test harness for catalog-test-agent. Run the following test cases in sequence.
For each case, spawn catalog-test-agent with the given prompt, capture the returned JSON,
and evaluate it against the assertions.

Test 1: happy path (all methods covered)
[prompt and assertions here]

Test 2: no testable methods
[prompt and assertions here]

Test 3: failing test (implementation bug)
[prompt and assertions here]

Return:
[{ "test": "...", "passed": true/false, "actual": {...}, "gap": "..." }]
```

A gap is a short description of what differed between actual and expected. Gaps are more useful than raw diffs because they name the behavior the agent failed to produce.

## Reading Failures as Improvement Signals

Each failed test points to a specific gap in the agent's body instructions. An agent that reports `"status": "pass"` when tests failed is ignoring the runner output; add an instruction: "Set status to 'fail' if dotnet test reports any failed tests." An agent that writes tests for private methods is missing a scope rule; add: "Only write tests for public methods." An agent that omits fields from the return schema needs an explicit template in the body with a fill-in-the-blank structure.

Run the updated agent against the same test case that failed. If it passes, the instruction worked. If it fails differently, the gap description tells you the next instruction to add.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/model` | Switch to Sonnet or Opus for test harness runs; stronger models evaluate agent output more reliably |
| `/cost` | Track token cost per test run; agent test suites are inexpensive and should be rerun freely after each body change |
| `/find-skills` | Discover pre-built agent skills with known behavior rather than authoring and testing one from scratch |

## Key Topics covered in this module

- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents): agent frontmatter fields, the Agent tool, and orchestration patterns
- [Claude Code Settings and Permissions](https://code.claude.com/docs/en/settings): configuring `tools:` allowlists and `permissions:` blocks
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview): model selection for test harnesses versus implementation agents
