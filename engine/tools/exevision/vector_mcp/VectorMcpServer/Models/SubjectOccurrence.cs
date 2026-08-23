using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("subject_occurrences")]
public class SubjectOccurrence
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("subject_id", TypeName = "text")]
    public string SubjectId { get; set; } = string.Empty;

    [Column("source_id", TypeName = "text")]
    public string? SourceId { get; set; }

    [Column("chapter", TypeName = "text")]
    public string? Chapter { get; set; }

    [Column("segment_label", TypeName = "text")]
    public string? SegmentLabel { get; set; }

    [Column("segment_type", TypeName = "text")]
    public string? SegmentType { get; set; }

    [Column("phase_id", TypeName = "text")]
    public string? PhaseId { get; set; }

    [Column("scene_label", TypeName = "text")]
    public string? SceneLabel { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
