using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace VectorMcpServer.Models;

[Table("subject_asset_links")]
public class SubjectAssetLink
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [Column("subject_id", TypeName = "text")]
    public string SubjectId { get; set; } = string.Empty;

    [Required]
    [Column("set_id")]
    public Guid SetId { get; set; }

    [Column("variant", TypeName = "text")]
    public string? Variant { get; set; }

    [Column("meta", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
