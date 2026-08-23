using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("asset_set_items")]
public class AssetSetItem
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("set_id")]
    public Guid SetId { get; set; }

    [Required]
    [Column("artifact_id")]
    public Guid ArtifactId { get; set; }

    [Column("role", TypeName = "text")]
    public string? Role { get; set; }

    [Column("ordinal")]
    public int? Ordinal { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
