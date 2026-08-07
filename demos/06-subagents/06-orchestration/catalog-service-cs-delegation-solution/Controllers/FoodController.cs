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
            if (item is null)
            {
                return NotFound();
            }
            return item;
        }

        // http://localhost:PORT/food
        [HttpPost()]
        public async Task<ActionResult<CatalogItem>> CreateFood(CatalogItem item)
        {
            if (!CatalogItemValidator.TryValidate(item, out var problem))
            {
                return BadRequest(problem);
            }

            ctx.Food.Add(item);
            await ctx.SaveChangesAsync();
            logger.LogEvent("CreateFood", item);
            return CreatedAtAction(nameof(GetById), new { id = item.ID }, item);
        }

        // http://localhost:PORT/food
        [HttpPut()]
        public async Task<ActionResult<CatalogItem>> UpdateFood(CatalogItem item)
        {
            if (!CatalogItemValidator.TryValidate(item, out var problem))
            {
                return BadRequest(problem);
            }

            var exists = await ctx.Food.AnyAsync(v => v.ID == item.ID);
            if (!exists)
            {
                return NotFound();
            }

            ctx.Food.Attach(item);
            ctx.Entry(item).State = EntityState.Modified;
            await ctx.SaveChangesAsync();
            logger.LogEvent("UpdateFood", item);
            return Ok(item);
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

            ctx.Remove(item);
            await ctx.SaveChangesAsync();
            logger.LogEvent("DeleteFood", id.ToString());
            return NoContent();
        }
    }
}
