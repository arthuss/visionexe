using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("artifacts")]
public class ArtifactRecord
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("kind", TypeName = "text")]
    public string Kind { get; set; } = string.Empty;

    [Column("sha256", TypeName = "text")]
    public string? Sha256 { get; set; }

    [Column("content", TypeName = "text")]
    public string? Content { get; set; }

    [Column("storage_path", TypeName = "text")]
    public string? StoragePath { get; set; }

    [Column("mime", TypeName = "text")]
    public string? Mime { get; set; }

    [Column("size_bytes")]
    public long? SizeBytes { get; set; }

    [Column("run_id")]
    public Guid? RunId { get; set; }

    [Column("story_id", TypeName = "text")]
    public string? StoryId { get; set; }

    [Column("timeline_id", TypeName = "text")]
    public string? TimelineId { get; set; }

    [Column("unit_ref", TypeName = "text")]
    public string? UnitRef { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
