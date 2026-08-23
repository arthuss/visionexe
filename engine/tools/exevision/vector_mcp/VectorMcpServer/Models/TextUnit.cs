using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("text_units")]
public class TextUnit
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("unit_ref", TypeName = "text")]
    public string UnitRef { get; set; } = string.Empty;

    [Column("story_id", TypeName = "text")]
    public string? StoryId { get; set; }

    [Column("timeline_id", TypeName = "text")]
    public string? TimelineId { get; set; }

    [Column("chapter_id", TypeName = "text")]
    public string? ChapterId { get; set; }

    [Column("segment_label", TypeName = "text")]
    public string? SegmentLabel { get; set; }

    [Column("segment_type", TypeName = "text")]
    public string? SegmentType { get; set; }

    [Column("verse_id", TypeName = "text")]
    public string? VerseId { get; set; }

    [Column("scene_id", TypeName = "text")]
    public string? SceneId { get; set; }

    [Required]
    [Column("content", TypeName = "text")]
    public string Content { get; set; } = string.Empty;

    [Column("sha256", TypeName = "text")]
    public string? Sha256 { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
