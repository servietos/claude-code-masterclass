namespace TodoApi.Models;

public class Todo
{
    public int Id { get; init; }
    public string Title { get; init; } = string.Empty;
    public bool Done { get; init; }
    public DateTime CreatedAt { get; init; }
}
