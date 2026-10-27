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

    private static FoodController NewController(FoodDBContext ctx)
    {
        var cfg = new ConfigurationBuilder().AddInMemoryCollection(new Dictionary<string, string?> { ["title"] = "test" }).Build();
        var logger = new AILogger(new TelemetryClient(new TelemetryConfiguration()), cfg);
        return new FoodController(ctx, logger);
    }

    [Fact]
    public async Task GetFood_ReturnsSeededItems()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetFood();
        Assert.Equal(5, result.Count());
    }

    [Fact]
    public async Task GetFood_EmptyTable_ReturnsEmptyList()
    {
        using var ctx = NewContext();
        ctx.Food.RemoveRange(ctx.Food);
        await ctx.SaveChangesAsync();
        var result = await NewController(ctx).GetFood();
        Assert.Empty(result);
    }

    [Fact]
    public async Task GetById_ExistingId_ReturnsItem()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetById(3);
        Assert.NotNull(result);
        Assert.Equal("Wiener Schnitzel", result.Name);
    }

    [Fact]
    public async Task GetById_UnknownId_ReturnsNull()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).GetById(999);
        Assert.Null(result);
    }

    [Fact]
    public async Task CreateFood_PersistsItem()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 100, Name = "Ramen", Price = 14, InStock = 3 };
        var result = await NewController(ctx).CreateFood(item);
        Assert.Equal(100, result.ID);
        Assert.Equal(6, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task CreateFood_DuplicateId_Throws()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 1, Name = "Duplicate", Price = 1, InStock = 1 };
        await Assert.ThrowsAnyAsync<Exception>(() => NewController(ctx).CreateFood(item));
    }

    [Fact]
    public async Task UpdateFood_ExistingItem_PersistsChanges()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 2, Name = "Renamed", Price = 20, InStock = 1, PictureUrl = "x.png", Description = "d" };
        var result = await NewController(ctx).UpdateFood(item);
        Assert.Equal("Renamed", result.Name);
        ctx.ChangeTracker.Clear();
        Assert.Equal("Renamed", (await ctx.Food.FindAsync(2))!.Name);
    }

    [Fact]
    public async Task UpdateFood_UnknownId_Throws()
    {
        using var ctx = NewContext();
        var item = new CatalogItem { ID = 999, Name = "Ghost", Price = 1, InStock = 1 };
        await Assert.ThrowsAsync<DbUpdateConcurrencyException>(() => NewController(ctx).UpdateFood(item));
    }

    [Fact]
    public async Task DeleteFood_ExistingId_RemovesItem()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).DeleteFood(4);
        Assert.IsType<OkResult>(result);
        Assert.Null(await ctx.Food.FindAsync(4));
        Assert.Equal(4, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task DeleteFood_UnknownId_ReturnsOkAndKeepsData()
    {
        using var ctx = NewContext();
        var result = await NewController(ctx).DeleteFood(999);
        Assert.IsType<OkResult>(result);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }
}
