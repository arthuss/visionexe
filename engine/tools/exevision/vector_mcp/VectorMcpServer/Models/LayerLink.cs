using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("layer_links")]
public class LayerLink
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("owner_kind", TypeName = "text")]
    public string OwnerKind { get; set; } = string.Empty;

    [Required]
    [Column("owner_id", TypeName = "text")]
    public string OwnerId { get; set; } = string.Empty;

    [Required]
    [Column("set_id")]
    public Guid SetId { get; set; }

    [Column("layer_type", TypeName = "text")]
    public string? LayerType { get; set; }

    [Column("role", TypeName = "text")]
    public string? Role { get; set; }

    [Column("scope", TypeName = "text")]
    public string? Scope { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
