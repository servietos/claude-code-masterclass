using System.Collections.Generic;
using System.Linq;
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

        [HttpGet("search")]
        public async Task<ActionResult<IEnumerable<CatalogItem>>> SearchFood([FromQuery] string name)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                return BadRequest();
            }
            var items = await ctx.Food
                .Where(f => EF.Functions.Like(f.Name, $"%{name}%"))
                .ToArrayAsync();
            return Ok(items);
        }

        // http://localhost:PORT/food/3
        [HttpGet("{id}")]
        public async Task<CatalogItem> GetById(int id)
        {
            return await ctx.Food.FirstOrDefaultAsync(v => v.ID == id);
        }

        // http://localhost:PORT/food
        [HttpPost()]
        public async Task<CatalogItem> CreateFood(CatalogItem item)
        {
            ctx.Food.Add(item);
            await ctx.SaveChangesAsync();
            return item;
        }

        // http://localhost:PORT/food
        [HttpPut()]
        public async Task<CatalogItem> UpdateFood(CatalogItem item)
        {
            ctx.Food.Attach(item);
            ctx.Entry(item).State = EntityState.Modified;
            await ctx.SaveChangesAsync();
            return item;
        }

        // http://localhost:PORT/food
        [HttpDelete("{id}")]
        public async Task<ActionResult> DeleteFood(int id)
        {
            var item = GetById(id);
            if (item != null)
            {
                ctx.Remove(item);
                await ctx.SaveChangesAsync();
            }
            return Ok();
        }
    }
}