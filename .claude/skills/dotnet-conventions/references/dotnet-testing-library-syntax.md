# xUnit, FluentAssertions and NSubstitute Syntax

## xUnit Attributes

| Attribute | When to use |
|---|---|
| `[Fact]` | Single, parameterless test case |
| `[Theory]` | Parameterized test with multiple inputs |
| `[InlineData(...)]` | Inline parameters for a `[Theory]` |

## FluentAssertions

| Assertion | Example |
|---|---|
| Equality | `result.Should().Be(expected)` |
| Null check | `result.Should().NotBeNull()` |
| Deep equality | `result.Should().BeEquivalentTo(expected)` |
| Collection not empty | `result.Should().NotBeEmpty()` |
| Type check | `result.Should().BeOfType<OkObjectResult>()` |

## NSubstitute

| Operation | Example |
|---|---|
| Create substitute | `var svc = Substitute.For<IMyService>()` |
| Stub return value | `svc.GetAsync(1).Returns(person)` |
| Verify call | `await svc.Received(1).SaveAsync(Arg.Any<Item>())` |
| Argument matcher | `Arg.Is<Item>(i => i.Name == "Widget")` |

Back to the index: [dotnet-testing](dotnet-testing.md)
