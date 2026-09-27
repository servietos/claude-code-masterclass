# Writing a Test Class

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

Back to the index: [dotnet-testing](dotnet-testing.md)
