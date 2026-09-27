# EF mapping for the shared-PK one-to-one blob table

## EF configuration: `WithOne` plus `HasForeignKey<TDependent>`

```csharp
public class ItemFile
{
    public Guid ItemId { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public int FileSize { get; set; }
    public byte[] Content { get; set; } = [];
}

public class ItemFileConfiguration : IEntityTypeConfiguration<ItemFile>
{
    public void Configure(EntityTypeBuilder<ItemFile> builder)
    {
        builder.ToTable("ItemFiles");
        builder.HasKey(f => f.ItemId);
        builder.Property(f => f.FileName).IsRequired().HasMaxLength(260);
        builder.Property(f => f.ContentType).IsRequired().HasMaxLength(100);
        builder.Property(f => f.Content).IsRequired();

        builder.HasOne<Item>()
               .WithOne()
               .HasForeignKey<ItemFile>(f => f.ItemId)
               .OnDelete(DeleteBehavior.Cascade);
    }
}
```

**This is where a copied sibling configuration goes wrong.** Every ordinary FK in the model reads
`HasOne<Parent>().WithMany().HasForeignKey(e => e.ParentId)`, and copying that shape here is the
natural mistake: `WithMany` makes it one-to-many, EF then wants a key of its own for the dependent,
and you get a shadow column beside the PK instead of the shared key you designed. A shared-PK
one-to-one needs both halves changed: `WithOne()`, and `HasForeignKey<TDependent>(...)` with the
**dependent** type as the generic argument.

Declaring no navigation property in either direction is deliberate. There is no `item.File` for an
`Include` to pull in, so the blob cannot be dragged into a query by habit or by a later refactor.

Back to the index: [sql-stored-files](sql-stored-files.md)
