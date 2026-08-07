# Catalog Service Search Endpoint Solution

Finished result of [Add a Search Endpoint with dotnet-expert](../demo-add-food-item-endpoint.md). This is a copy of this topic's own [catalog-service-cs](../catalog-service-cs/readme.md) starter with the `SearchFood` action added to `Controllers/FoodController.cs`.

## Run it

```bash
dotnet restore
dotnet run
```

The API listens on `http://localhost:5000`.

```bash
curl "http://localhost:5000/food/search?name=pi"
curl -i "http://localhost:5000/food/search"
```

The first call returns `Pizza Tartufo`, the second returns HTTP 400.
