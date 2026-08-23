using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("run_outputs")]
public class RunOutput
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("run_id")]
    public Guid RunId { get; set; }

    [Required]
    [Column("artifact_id")]
    public Guid ArtifactId { get; set; }

    [Required]
    [Column("role", TypeName = "text")]
    public string Role { get; set; } = string.Empty;

    [Column("ordinal")]
    public int? Ordinal { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
