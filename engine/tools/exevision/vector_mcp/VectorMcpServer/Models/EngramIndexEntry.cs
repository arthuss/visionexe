using System;

namespace VectorMcpServer.Models;

public sealed class EngramIndexEntry
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid DocumentId { get; set; }
    public string Collection { get; set; } = string.Empty;
    public int LayerId { get; set; }
    public long[] Hashes { get; set; } = Array.Empty<long>();
    public int TokenCount { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
