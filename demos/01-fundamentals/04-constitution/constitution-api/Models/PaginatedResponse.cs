namespace TodoApi.Models;

public record PaginatedResponse<T>(
    IReadOnlyList<T> Data,
    int Page,
    int Size,
    int Total,
    bool HasNext
);
