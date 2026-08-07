using Microsoft.AspNetCore.Mvc;
using TodoApi.Models;

namespace TodoApi.Controllers;

[ApiController]
[Route("[controller]")]
public class TodosController : ControllerBase
{
    private static readonly IReadOnlyList<Todo> _todos =
    [
        new Todo { Id = 1, Title = "Buy groceries", Done = true, CreatedAt = DateTime.UtcNow.AddDays(-5) },
        new Todo { Id = 2, Title = "Write tests", Done = false, CreatedAt = DateTime.UtcNow.AddDays(-4) },
        new Todo { Id = 3, Title = "Review PR", Done = false, CreatedAt = DateTime.UtcNow.AddDays(-3) },
        new Todo { Id = 4, Title = "Deploy to staging", Done = false, CreatedAt = DateTime.UtcNow.AddDays(-2) },
        new Todo { Id = 5, Title = "Update docs", Done = false, CreatedAt = DateTime.UtcNow.AddDays(-1) },
    ];

    [HttpGet]
    public ActionResult<PaginatedResponse<Todo>> GetTodos([FromQuery] int page = 1, [FromQuery] int size = 20)
    {
        var total = _todos.Count;
        var data = _todos.Skip((page - 1) * size).Take(size).ToList();
        var hasNext = page * size < total;

        return Ok(new PaginatedResponse<Todo>(data, page, size, total, hasNext));
    }
}
