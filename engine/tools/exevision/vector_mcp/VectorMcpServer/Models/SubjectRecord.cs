using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("subjects")]
public class SubjectRecord
{
    [Key]
    [Column("id", TypeName = "text")]
    public string Id { get; set; } = string.Empty;

    [Required]
    [Column("name", TypeName = "text")]
    public string Name { get; set; } = string.Empty;

    [Column("subject_type", TypeName = "text")]
    public string? SubjectType { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
