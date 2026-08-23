using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("analysis_artifacts")]
public class AnalysisArtifact
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("text_unit_id")]
    public Guid? TextUnitId { get; set; }

    [Column("analysis_type", TypeName = "text")]
    public string? AnalysisType { get; set; }

    [Column("artifact_id")]
    public Guid? ArtifactId { get; set; }

    [Column("content", TypeName = "text")]
    public string? Content { get; set; }

    [Column("sha256", TypeName = "text")]
    public string? Sha256 { get; set; }

    [Column("prompt_bundle_sha", TypeName = "text")]
    public string? PromptBundleSha { get; set; }

    [Column("model_id", TypeName = "text")]
    public string? ModelId { get; set; }

    [Column("settings", TypeName = "jsonb")]
    public Dictionary<string, object> Settings { get; set; } = new();

    [Column("run_id")]
    public Guid? RunId { get; set; }

    [Column("supersedes_id")]
    public Guid? SupersedesId { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
