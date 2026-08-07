using Microsoft.AspNetCore.Mvc;
using TodoApi.Models;

namespace TodoApi.Controllers;

[ApiController]
[Route("[controller]")]
public class UsersController : ControllerBase
{
    private static readonly IReadOnlyList<User> _users =
    [
        new User { Id = 1, Name = "Alice", Email = "alice@example.com" },
        new User { Id = 2, Name = "Bob", Email = "bob@example.com" },
        new User { Id = 3, Name = "Carol", Email = "carol@example.com" },
    ];

    [HttpGet]
    public ActionResult<PaginatedResponse<User>> GetUsers([FromQuery] int page = 1, [FromQuery] int size = 20)
    {
        var total = _users.Count;
        var data = _users.Skip((page - 1) * size).Take(size).ToList();
        var hasNext = page * size < total;

        return Ok(new PaginatedResponse<User>(data, page, size, total, hasNext));
    }
}
