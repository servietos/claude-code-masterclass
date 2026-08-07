# .NET Testing Patterns

Reference for xUnit, FluentAssertions, and NSubstitute. Target 80%+ behavior-focused coverage.

## Test Class Structure

```csharp
public class ItemsControllerTests
{
    private readonly AppDbContext _db = Substitute.For<AppDbContext>();

    [Fact]
    public async Task GetAll_ReturnsAllItems()
    {
        // Arrange
        var items = new List<Item> { new() { Id = 1, Name = "Widget" } }.AsQueryable();
        _db.Items.Returns(items);

        // Act
        var controller = new ItemsController(_db);
        var result = await controller.GetAll();

        // Assert
        result.Should().NotBeNull();
    }

    [Theory]
    [InlineData(1, true)]
    [InlineData(99, false)]
    public async Task GetById_ReturnsExpectedResult(int id, bool exists)
    {
        // Arrange / Act / Assert as needed
    }
}
```

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

## Controller Test with Mocked DbContext

```csharp
public class ItemsControllerServiceTests
{
    private readonly IAppDbContext _db = Substitute.For<IAppDbContext>();

    [Fact]
    public async Task GetAll_ReturnsItems()
    {
        _db.Items.Returns(new List<Item> { new() { Id = 1, Name = "Widget" } }.AsQueryable());
        var controller = new ItemsController(_db);
        var result = await controller.GetAll();
        result.Should().NotBeNull();
    }
}
```

## Coverage Goal

- 80%+ behavior-focused coverage.
- Test behavior, not implementation details.
- Cover both success paths and failure/not-found paths.
