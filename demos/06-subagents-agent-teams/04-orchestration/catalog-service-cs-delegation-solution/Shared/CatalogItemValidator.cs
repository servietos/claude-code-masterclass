using System.Collections.Generic;

namespace FoodApp
{
    public static class CatalogItemValidator
    {
        public static Dictionary<string, string[]> Validate(CatalogItem item)
        {
            var errors = new Dictionary<string, string[]>();

            if (item is null)
            {
                errors[nameof(CatalogItem)] = ["The item is required."];
                return errors;
            }

            if (string.IsNullOrWhiteSpace(item.Name))
            {
                errors[nameof(CatalogItem.Name)] = ["Name must not be empty."];
            }

            if (item.Price < 0)
            {
                errors[nameof(CatalogItem.Price)] = ["Price must not be negative."];
            }

            if (item.InStock < 0)
            {
                errors[nameof(CatalogItem.InStock)] = ["InStock must not be negative."];
            }

            return errors;
        }
    }
}
