using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("asset_sets")]
public class AssetSet
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("story_id", TypeName = "text")]
    public string? StoryId { get; set; }

    [Column("timeline_id", TypeName = "text")]
    public string? TimelineId { get; set; }

    [Column("chapter_id", TypeName = "text")]
    public string? ChapterId { get; set; }

    [Column("segment_label", TypeName = "text")]
    public string? SegmentLabel { get; set; }

    [Column("subject_id", TypeName = "text")]
    public string? SubjectId { get; set; }

    [Column("scene_id", TypeName = "text")]
    public string? SceneId { get; set; }

    [Column("label", TypeName = "text")]
    public string? Label { get; set; }

    [Column("set_type", TypeName = "text")]
    public string? SetType { get; set; }

    [Column("variant", TypeName = "text")]
    public string? Variant { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
