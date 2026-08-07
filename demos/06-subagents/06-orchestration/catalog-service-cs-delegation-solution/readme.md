# Catalog Service - App Modernization

A .NET 10 ASP.NET Core catalog API backed by EF Core and the seeded `food.db` SQLite file. `FoodController` serves `/food`, and it is the starter the demos in this topic extend.

This copy is the finished result of [`demo-delegation-fan-out.md`](../demo-delegation-fan-out.md): two agents fanned out from one coordinator prompt, one owning `Controllers/` and `Shared/`, the other owning `test-controllers.http`.
