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

        // http://localhost:PORT/food/3
        [HttpGet("{id}")]
        public async Task<ActionResult<CatalogItem>> GetById(int id)
        {
            var item = await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
            if (item == null)
            {
                return NotFound();
            }
            return item;
        }

        // http://localhost:PORT/food
        [HttpPost()]
        public async Task<ActionResult<CatalogItem>> CreateFood(CatalogItem item)
        {
            if (IsInvalid(item))
            {
                return Problem(title: "Invalid CatalogItem", statusCode: StatusCodes.Status400BadRequest);
            }
            ctx.Food.Add(item);
            await ctx.SaveChangesAsync();
            return CreatedAtAction(nameof(GetById), new { id = item.ID }, item);
        }

        // http://localhost:PORT/food
        [HttpPut()]
        public async Task<ActionResult<CatalogItem>> UpdateFood(CatalogItem item)
        {
            if (IsInvalid(item))
            {
                return Problem(title: "Invalid CatalogItem", statusCode: StatusCodes.Status400BadRequest);
            }
            if (!await ctx.Food.AnyAsync(v => v.ID == item.ID))
            {
                return NotFound();
            }
            ctx.Food.Update(item);
            await ctx.SaveChangesAsync();
            return Ok(item);
        }

        // http://localhost:PORT/food/3
        [HttpDelete("{id}")]
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

        private static bool IsInvalid(CatalogItem item)
        {
            return item == null || string.IsNullOrWhiteSpace(item.Name) || item.Price < 0 || item.InStock < 0;
        }
    }
}