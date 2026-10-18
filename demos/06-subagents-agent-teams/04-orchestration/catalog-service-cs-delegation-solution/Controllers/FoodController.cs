using System.Collections.Generic;
using System.Threading.Tasks;
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
            return item is null ? NotFound() : item;
        }

        // http://localhost:PORT/food
        [HttpPost()]
        public async Task<ActionResult<CatalogItem>> CreateFood(CatalogItem item)
        {
            var errors = CatalogItemValidator.Validate(item);
            if (errors.Count > 0)
            {
                return BadRequest(new ValidationProblemDetails(errors));
            }

            ctx.Food.Add(item);
            await ctx.SaveChangesAsync();
            return CreatedAtAction(nameof(GetById), new { id = item.ID }, item);
        }

        // http://localhost:PORT/food
        [HttpPut()]
        public async Task<ActionResult<CatalogItem>> UpdateFood(CatalogItem item)
        {
            var errors = CatalogItemValidator.Validate(item);
            if (errors.Count > 0)
            {
                return BadRequest(new ValidationProblemDetails(errors));
            }

            var existing = await ctx.Food.FirstOrDefaultAsync(v => v.ID == item.ID);
            if (existing is null)
            {
                return NotFound();
            }

            ctx.Entry(existing).CurrentValues.SetValues(item);
            await ctx.SaveChangesAsync();
            return Ok(existing);
        }

        // http://localhost:PORT/food
        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteFood(int id)
        {
            var item = await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
            if (item is null)
            {
                return NotFound();
            }

            ctx.Food.Remove(item);
            await ctx.SaveChangesAsync();
            return NoContent();
        }
    }
}