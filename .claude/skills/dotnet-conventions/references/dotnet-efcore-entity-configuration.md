# EF Core: entity configuration

## Entity Configuration

Use `IEntityTypeConfiguration<T>` for all model configuration. Never place data annotations on domain model classes.

```csharp
public class ItemConfiguration : IEntityTypeConfiguration<Item>
{
    public void Configure(EntityTypeBuilder<Item> builder)
    {
        builder.HasKey(i => i.Id);
        builder.Property(i => i.Name).IsRequired().HasMaxLength(200);
    }
}
```

A one-to-one where the dependent's primary key *is* the foreign key needs `WithOne()` and
`HasForeignKey<TDependent>(...)`, not the `WithMany()` every other configuration in the model uses:
see [`sql-stored-files`](sql-stored-files.md).

Apply in `OnModelCreating`:

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

Back to the index: [dotnet-efcore](dotnet-efcore.md)
