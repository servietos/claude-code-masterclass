using FoodApp;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;

namespace catalog_service_cs.Tests;

public class FoodControllerTests
{
    private static FoodDBContext NewContext()
    {
        var options = new DbContextOptionsBuilder<FoodDBContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        var ctx = new FoodDBContext(options);
        ctx.Database.EnsureCreated();
        return ctx;
    }

    private static AILogger NewLogger()
    {
        var telemetry = new TelemetryClient(new TelemetryConfiguration { DisableTelemetry = true });
        var cfg = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?> { ["title"] = "tests" }).Build();
        return new AILogger(telemetry, cfg);
    }

    private static FoodController NewController(FoodDBContext ctx) => new(ctx, NewLogger());

    [Fact]
    public async Task GetFood_WithSeededItems_ReturnsAllItems()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetFood();
        Assert.Equal(5, result.Count());
    }

    [Fact]
    public async Task GetById_WithExistingId_ReturnsItem()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetById(1);
        Assert.Equal("Hand pulled Noodles", result.Name);
    }

    [Fact]
    public async Task GetById_WithUnknownId_ReturnsNull()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetById(999);
        Assert.Null(result);
    }

    [Fact]
    public async Task CreateFood_WithNewItem_PersistsAndReturnsItem()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 6, Name = "Ramen", Price = 14, InStock = 3, PictureUrl = "ramen.png", Description = "Tonkotsu ramen." };
        var result = await NewController(ctx).CreateFood(item);
        Assert.Equal(6, result.ID);
        Assert.Equal(6, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task UpdateFood_WithModifiedItem_SavesChanges()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 2, Name = "Pad Kra Pao XL", Price = 19, InStock = 5, PictureUrl = "pad-kra-pao.png", Description = "Bigger portion." };
        var result = await NewController(ctx).UpdateFood(item);
        Assert.Equal("Pad Kra Pao XL", result.Name);
    }

    [Fact]
    public async Task DeleteFood_WithExistingId_ThrowsBecauseGetByIdIsNotAwaited()
    {
        using var ctx = NewContext();
        var controller = NewController(ctx);
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(() => controller.DeleteFood(3));
        Assert.Contains("Task<CatalogItem>", ex.Message);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task DeleteFood_WithUnknownId_ThrowsBecauseGetByIdIsNotAwaited()
    {
        using var ctx = NewContext();
        var controller = NewController(ctx);
        await Assert.ThrowsAsync<InvalidOperationException>(() => controller.DeleteFood(999));
    }
}
