using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace FoodApp
{
    [Route("[controller]")]
    [ApiController]
    public class FoodController(FoodDBContext ctx, AILogger logger) : ControllerBase
    {

        // http://localhost:PORT/food
        [HttpGet()]
        public async Task<IEnumerable<CatalogItem>> GetFood()
        {
            logger.LogEvent("GetFood", "test");
            return await ctx.Food.ToArrayAsync();
        }

        /// <summary>
        /// Retrieves a single catalog item by its numeric ID.
        /// </summary>
        /// <param name="id">The numeric ID of the catalog item.</param>
        /// <returns>The matching catalog item, or 404 when no item with that ID exists.</returns>
        // http://localhost:PORT/food/3
        [HttpGet("{id:int}")]
        public async Task<ActionResult<CatalogItem>> GetById(int id)
        {
            var item = await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
            if (item == null)
            {
                return NotFound();
            }
            return Ok(item);
        }

        /// <summary>
        /// Creates a new catalog item.
        /// </summary>
        /// <param name="item">The catalog item to create.</param>
        /// <returns>201 with a Location header when created, 400 when validation fails, 409 when the ID already exists.</returns>
        // http://localhost:PORT/food
        [HttpPost()]
        public async Task<ActionResult<CatalogItem>> CreateFood(CatalogItem item)
        {
            var validationProblem = ValidateCatalogItem(item);
            if (validationProblem != null)
            {
                return validationProblem;
            }

            var duplicateExists = await ctx.Food.AnyAsync(v => v.ID == item.ID);
            if (duplicateExists)
            {
                return ConflictResponse(item.ID);
            }

            try
            {
                ctx.Food.Add(item);
                await ctx.SaveChangesAsync();
            }
            catch (DbUpdateException)
            {
                return ConflictResponse(item.ID);
            }

            return CreatedAtAction(nameof(GetById), new { id = item.ID }, item);
        }

        /// <summary>
        /// Replaces an existing catalog item with the supplied values.
        /// </summary>
        /// <param name="item">The catalog item values to apply.</param>
        /// <returns>200 with the updated item, 400 when validation fails, 404 when no item with that ID exists.</returns>
        // http://localhost:PORT/food
        [HttpPut()]
        public async Task<ActionResult<CatalogItem>> UpdateFood(CatalogItem item)
        {
            var validationProblem = ValidateCatalogItem(item);
            if (validationProblem != null)
            {
                return validationProblem;
            }

            var existingItem = await ctx.Food.FirstOrDefaultAsync(v => v.ID == item.ID);
            if (existingItem == null)
            {
                return NotFound();
            }

            existingItem.Name = item.Name;
            existingItem.Price = item.Price;
            existingItem.InStock = item.InStock;
            existingItem.PictureUrl = item.PictureUrl;
            existingItem.Description = item.Description;

            await ctx.SaveChangesAsync();
            return Ok(existingItem);
        }

        /// <summary>
        /// Deletes the catalog item with the given ID.
        /// </summary>
        /// <param name="id">The numeric ID of the catalog item to delete.</param>
        /// <returns>204 when deleted, 404 when no item with that ID exists.</returns>
        // http://localhost:PORT/food/3
        [HttpDelete("{id:int}")]
        public async Task<ActionResult> DeleteFood(int id)
        {
            var item = await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
            if (item == null)
            {
                return NotFound();
            }

            ctx.Food.Remove(item);
            await ctx.SaveChangesAsync();
            return NoContent();
        }

        /// <summary>
        /// Validates a catalog item and returns a problem+json response identifying the first
        /// failing rule, or null when the item is valid.
        /// </summary>
        /// <param name="item">The catalog item to validate.</param>
        /// <returns>An <see cref="ObjectResult"/> carrying a problem+json body when invalid; otherwise null.</returns>
        private static ObjectResult ValidateCatalogItem(CatalogItem item)
        {
            if (item == null)
            {
                return ProblemResponse("Request body must not be empty.");
            }
            if (string.IsNullOrWhiteSpace(item.Name))
            {
                return ProblemResponse("Name must not be empty.");
            }
            if (item.Price < 0)
            {
                return ProblemResponse("Price must not be negative.");
            }
            if (item.InStock < 0)
            {
                return ProblemResponse("InStock must not be negative.");
            }
            return null;
        }

        /// <summary>
        /// Builds a 400 Bad Request result whose body is serialized as application/problem+json.
        /// </summary>
        /// <param name="detail">A message identifying the specific rule that failed.</param>
        /// <returns>An <see cref="ObjectResult"/> carrying the problem+json body.</returns>
        private static ObjectResult ProblemResponse(string detail)
        {
            return new ObjectResult(new ProblemDetails
            {
                Status = StatusCodes.Status400BadRequest,
                Title = "Invalid catalog item.",
                Detail = detail
            })
            {
                StatusCode = StatusCodes.Status400BadRequest,
                ContentTypes = { "application/problem+json" }
            };
        }

        /// <summary>
        /// Builds a 409 Conflict result whose body is serialized as application/problem+json.
        /// </summary>
        /// <param name="id">The ID of the catalog item that already exists.</param>
        /// <returns>An <see cref="ObjectResult"/> carrying the problem+json body.</returns>
        private static ObjectResult ConflictResponse(int id)
        {
            return new ObjectResult(new ProblemDetails
            {
                Status = StatusCodes.Status409Conflict,
                Title = "Duplicate catalog item.",
                Detail = $"An item with ID {id} already exists."
            })
            {
                StatusCode = StatusCodes.Status409Conflict,
                ContentTypes = { "application/problem+json" }
            };
        }
    }
}