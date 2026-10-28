using FoodApp;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;

namespace catalog_service_cs.Tests;

public class FoodControllerTests
{
    private static FoodController CreateController(out FoodDBContext ctx)
    {
        var options = new DbContextOptionsBuilder<FoodDBContext>()
            .UseInMemoryDatabase($"food-{Guid.NewGuid()}")
            .Options;
        ctx = new FoodDBContext(options);
        ctx.Database.EnsureCreated();

        var telemetryConfig = new TelemetryConfiguration { DisableTelemetry = true };
        var client = new TelemetryClient(telemetryConfig);
        var cfg = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?> { { "title", "Food" } })
            .Build();

        return new FoodController(ctx, new AILogger(client, cfg));
    }

    [Fact]
    public async Task GetFood_SeededDatabase_ReturnsFiveSeededItems()
    {
        var controller = CreateController(out _);

        var result = (await controller.GetFood()).ToList();

        Assert.Equal(5, result.Count);
        Assert.Contains(result, i => i.Name == "Wiener Schnitzel");
    }

    [Fact]
    public async Task GetById_ExistingId_ReturnsMatchingItem()
    {
        var controller = CreateController(out _);

        var result = await controller.GetById(3);

        Assert.NotNull(result);
        Assert.Equal("Wiener Schnitzel", result.Name);
        Assert.Equal(18m, result.Price);
    }

    [Fact]
    public async Task GetById_UnknownId_ReturnsNull()
    {
        var controller = CreateController(out _);

        var result = await controller.GetById(999);

        Assert.Null(result);
    }

    [Fact]
    public async Task CreateFood_NewItem_PersistsAndAssignsId()
    {
        var controller = CreateController(out var ctx);
        var item = new CatalogItem { Name = "Ramen", Price = 14m, InStock = 7, PictureUrl = "ramen.png", Description = "Noodle soup" };

        var created = await controller.CreateFood(item);

        Assert.NotEqual(0, created.ID);
        Assert.Equal(6, await ctx.Food.CountAsync());
        Assert.NotNull(await ctx.Food.FindAsync(created.ID));
    }

    [Fact]
    public async Task UpdateFood_ExistingItem_PersistsChanges()
    {
        var controller = CreateController(out var ctx);
        var item = new CatalogItem { ID = 2, Name = "Pad Kra Pao Deluxe", Price = 20m, InStock = 1, PictureUrl = "pad-kra-pao.png", Description = "Updated" };

        var updated = await controller.UpdateFood(item);

        Assert.Equal("Pad Kra Pao Deluxe", updated.Name);
        ctx.ChangeTracker.Clear();
        var stored = await ctx.Food.SingleAsync(f => f.ID == 2);
        Assert.Equal("Pad Kra Pao Deluxe", stored.Name);
        Assert.Equal(20m, stored.Price);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task DeleteFood_ExistingId_ThrowsInvalidOperationException()
    {
        var controller = CreateController(out _);

        await Assert.ThrowsAsync<InvalidOperationException>(() => controller.DeleteFood(1));
    }

    [Fact]
    public async Task DeleteFood_UnknownId_ThrowsInvalidOperationException()
    {
        var controller = CreateController(out _);

        await Assert.ThrowsAsync<InvalidOperationException>(() => controller.DeleteFood(999));
    }
}
