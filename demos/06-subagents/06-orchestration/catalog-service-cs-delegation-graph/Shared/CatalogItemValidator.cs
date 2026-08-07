using Microsoft.AspNetCore.Mvc.ModelBinding;

namespace FoodApp
{
    /// <summary>
    /// Validates a <see cref="CatalogItem"/> against the write-path rules shared by
    /// the create and update endpoints of <see cref="FoodController"/>.
    /// </summary>
    public static class CatalogItemValidator
    {
        /// <summary>
        /// Adds a model error for every rule the given <paramref name="item"/> violates.
        /// A caller inspects <paramref name="modelState"/>.IsValid after calling this method.
        /// </summary>
        /// <param name="item">The catalog item submitted by the client.</param>
        /// <param name="modelState">The model state the errors are recorded into.</param>
        public static void Validate(CatalogItem item, ModelStateDictionary modelState)
        {
            if (item is null)
            {
                modelState.AddModelError(nameof(CatalogItem), "Item is required.");
                return;
            }

            if (string.IsNullOrWhiteSpace(item.Name))
                modelState.AddModelError(nameof(CatalogItem.Name), "Name is required.");

            if (item.Price < 0)
                modelState.AddModelError(nameof(CatalogItem.Price), "Price cannot be negative.");

            if (item.InStock < 0)
                modelState.AddModelError(nameof(CatalogItem.InStock), "InStock cannot be negative.");
        }
    }
}
