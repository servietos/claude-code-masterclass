using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace FoodApp
{
    /// <summary>
    /// Persists customer identity and shipping address captured by the checkout form.
    /// </summary>
    [Route("api/[controller]")]
    [ApiController]
    public class CustomersController(FoodDBContext ctx, ILogger<CustomersController> logger) : ControllerBase
    {
        /// <summary>
        /// Saves a customer submitted by the checkout form.
        /// </summary>
        /// <param name="customer">The customer payload sent by the client.</param>
        /// <returns>The persisted customer with its generated identifier.</returns>
        [HttpPost]
        public async Task<ActionResult<Customer>> CreateCustomer([FromBody] Customer customer)
        {
            customer.CreatedAt = DateTime.UtcNow;
            ctx.Customers.Add(customer);
            await ctx.SaveChangesAsync().ConfigureAwait(false);
            logger.LogInformation("Saved customer {CustomerId} for {Email}", customer.Id, customer.Email);
            return CreatedAtAction(nameof(CreateCustomer), new { id = customer.Id }, customer);
        }
    }
}
