using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("runs")]
public class RunRecord
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("run_type", TypeName = "text")]
    public string RunType { get; set; } = string.Empty;

    [Column("story_id", TypeName = "text")]
    public string? StoryId { get; set; }

    [Column("timeline_id", TypeName = "text")]
    public string? TimelineId { get; set; }

    [Column("unit_ref", TypeName = "text")]
    public string? UnitRef { get; set; }

    [Column("input_sha256", TypeName = "text")]
    public string? InputSha256 { get; set; }

    [Column("prompt_bundle_sha", TypeName = "text")]
    public string? PromptBundleSha { get; set; }

    [Column("model_id", TypeName = "text")]
    public string? ModelId { get; set; }

    [Column("settings", TypeName = "jsonb")]
    public Dictionary<string, object> Settings { get; set; } = new();

    [Column("inputs", TypeName = "jsonb")]
    public Dictionary<string, object> Inputs { get; set; } = new();

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
