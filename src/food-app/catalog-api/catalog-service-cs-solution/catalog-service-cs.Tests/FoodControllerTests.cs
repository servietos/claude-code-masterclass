using FoodApp;
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;

namespace CatalogService.Tests;

public class FoodControllerTests
{
    private static FoodDBContext NewContext(string name)
    {
        var options = new DbContextOptionsBuilder<FoodDBContext>()
            .UseInMemoryDatabase(name)
            .Options;
        var ctx = new FoodDBContext(options);
        ctx.Database.EnsureCreated();
        return ctx;
    }

    private static AILogger NewLogger()
    {
        var cfg = new ConfigurationBuilder()
            .AddInMemoryCollection(new Dictionary<string, string?> { ["title"] = "catalog-tests" })
            .Build();
        var telemetry = TelemetryConfiguration.CreateDefault();
        telemetry.DisableTelemetry = true;
        return new AILogger(new TelemetryClient(telemetry), cfg);
    }

    private static FoodController NewController(FoodDBContext ctx) => new(ctx, NewLogger());

    [Fact]
    public async Task GetFood_WithSeededCatalog_ReturnsEveryCatalogItem()
    {
        using var ctx = NewContext(nameof(GetFood_WithSeededCatalog_ReturnsEveryCatalogItem));
        var result = (await NewController(ctx).GetFood()).ToList();

        Assert.Equal(5, result.Count);
        Assert.Equal(
            new[] { 1, 2, 3, 4, 5 },
            result.Select(i => i.ID).OrderBy(i => i).ToArray());
        Assert.Contains(result, i => i.Name == "Wiener Schnitzel" && i.Price == 18m);
    }

    [Fact]
    public async Task GetFood_WithEmptyCatalog_ReturnsEmptySequence()
    {
        using var ctx = NewContext(nameof(GetFood_WithEmptyCatalog_ReturnsEmptySequence));
        ctx.Food.RemoveRange(ctx.Food);
        await ctx.SaveChangesAsync();

        var result = await NewController(ctx).GetFood();

        Assert.Empty(result);
    }

    [Fact]
    public async Task GetById_WithExistingId_ReturnsThatItemWithAllFields()
    {
        using var ctx = NewContext(nameof(GetById_WithExistingId_ReturnsThatItemWithAllFields));

        var result = await NewController(ctx).GetById(2);

        Assert.NotNull(result);
        Assert.Equal(2, result.ID);
        Assert.Equal("Pad Kra Pao", result.Name);
        Assert.Equal(16m, result.Price);
        Assert.Equal(12, result.InStock);
        Assert.Equal("pad-kra-pao.png", result.PictureUrl);
    }

    [Fact]
    public async Task GetById_WithUnknownId_ReturnsNull()
    {
        using var ctx = NewContext(nameof(GetById_WithUnknownId_ReturnsNull));

        var result = await NewController(ctx).GetById(9999);

        Assert.Null(result);
    }

    [Fact]
    public async Task CreateFood_WithNewItem_PersistsItemAndReturnsIt()
    {
        using var ctx = NewContext(nameof(CreateFood_WithNewItem_PersistsItemAndReturnsIt));
        var item = new CatalogItem { Name = "Ramen", Price = 14.5m, InStock = 7, PictureUrl = "ramen.png", Description = "Tonkotsu" };

        var returned = await NewController(ctx).CreateFood(item);

        var stored = await ctx.Food.SingleAsync(i => i.Name == "Ramen");
        Assert.Equal(stored.ID, returned.ID);
        Assert.Equal(14.5m, stored.Price);
        Assert.Equal(7, stored.InStock);
        Assert.Equal(6, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task CreateFood_WithUnsetId_AssignsGeneratedKey()
    {
        using var ctx = NewContext(nameof(CreateFood_WithUnsetId_AssignsGeneratedKey));
        var item = new CatalogItem { ID = 0, Name = "Bibimbap", Price = 15m };

        var returned = await NewController(ctx).CreateFood(item);

        Assert.NotEqual(0, returned.ID);
        Assert.DoesNotContain(new[] { 1, 2, 3, 4, 5 }, id => id == returned.ID);
    }

    [Fact]
    public async Task UpdateFood_WithChangedFields_WritesThemToTheStore()
    {
        using var ctx = NewContext(nameof(UpdateFood_WithChangedFields_WritesThemToTheStore));
        var edited = new CatalogItem
        {
            ID = 3,
            Name = "Wiener Schnitzel XL",
            Price = 22.5m,
            InStock = 2,
            PictureUrl = "schnitzel.jpg",
            Description = "Bigger"
        };

        var returned = await NewController(ctx).UpdateFood(edited);

        var stored = await ctx.Food.AsNoTracking().SingleAsync(i => i.ID == 3);
        Assert.Equal("Wiener Schnitzel XL", stored.Name);
        Assert.Equal(22.5m, stored.Price);
        Assert.Equal(2, stored.InStock);
        Assert.Equal(3, returned.ID);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task UpdateFood_WithUnknownId_ThrowsConcurrencyExceptionAndStoresNothing()
    {
        using var ctx = NewContext(nameof(UpdateFood_WithUnknownId_ThrowsConcurrencyExceptionAndStoresNothing));
        var ghost = new CatalogItem { ID = 4242, Name = "Ghost", Price = 1m };

        await Assert.ThrowsAsync<DbUpdateConcurrencyException>(() => NewController(ctx).UpdateFood(ghost));

        Assert.Equal(5, await ctx.Food.CountAsync());
        Assert.Null(await ctx.Food.AsNoTracking().FirstOrDefaultAsync(i => i.ID == 4242));
    }

    [Fact]
    public async Task DeleteFood_WithExistingId_RemovesThatItemOnly()
    {
        using var ctx = NewContext(nameof(DeleteFood_WithExistingId_RemovesThatItemOnly));

        var result = await NewController(ctx).DeleteFood(1);

        Assert.IsType<OkResult>(result);
        Assert.Null(await ctx.Food.AsNoTracking().FirstOrDefaultAsync(i => i.ID == 1));
        Assert.Equal(4, await ctx.Food.CountAsync());
    }

    [Fact]
    public async Task DeleteFood_WithUnknownId_LeavesTheCatalogUnchanged()
    {
        using var ctx = NewContext(nameof(DeleteFood_WithUnknownId_LeavesTheCatalogUnchanged));

        var result = await NewController(ctx).DeleteFood(9999);

        Assert.IsType<OkResult>(result);
        Assert.Equal(5, await ctx.Food.CountAsync());
    }
}
