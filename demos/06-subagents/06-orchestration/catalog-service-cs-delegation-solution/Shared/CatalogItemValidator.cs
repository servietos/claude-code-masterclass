using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;

namespace FoodApp
{
    /// <summary>
    /// Validates <see cref="CatalogItem"/> instances before they are written to the catalog store.
    /// </summary>
    public static class CatalogItemValidator
    {
        /// <summary>
        /// Validates the supplied <see cref="CatalogItem"/> against the catalog write-path rules:
        /// <see cref="CatalogItem.Name"/> must not be null, empty or whitespace, and
        /// <see cref="CatalogItem.Price"/> and <see cref="CatalogItem.InStock"/> must not be negative.
        /// </summary>
        /// <param name="item">The catalog item to validate.</param>
        /// <param name="problem">
        /// When this method returns <see langword="false"/>, a <see cref="ProblemDetails"/> describing
        /// the validation failure; otherwise <see langword="null"/>.
        /// </param>
        /// <returns><see langword="true"/> when <paramref name="item"/> is valid; otherwise <see langword="false"/>.</returns>
        public static bool TryValidate(CatalogItem item, out ProblemDetails problem)
        {
            if (item is null)
            {
                problem = CreateProblem("The request body must contain a catalog item.");
                return false;
            }

            if (string.IsNullOrWhiteSpace(item.Name))
            {
                problem = CreateProblem("Name is required and cannot be empty or whitespace.");
                return false;
            }

            if (item.Price < 0)
            {
                problem = CreateProblem("Price cannot be negative.");
                return false;
            }

            if (item.InStock < 0)
            {
                problem = CreateProblem("InStock cannot be negative.");
                return false;
            }

            problem = null;
            return true;
        }

        private static ProblemDetails CreateProblem(string detail)
        {
            return new ProblemDetails
            {
                Title = "Invalid catalog item",
                Detail = detail,
                Status = StatusCodes.Status400BadRequest
            };
        }
    }
}
