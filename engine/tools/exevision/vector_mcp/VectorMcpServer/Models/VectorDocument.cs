using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Microsoft.EntityFrameworkCore;
using Pgvector;

namespace VectorMcpServer.Models;

/// <summary>
/// Vector Document Model - Compatible with ExegetOS Core architecture
/// Maps to PostgreSQL table with pgvector embeddings
/// </summary>
[Table("vector_documents")]
[Index(nameof(Collection))]
public class VectorDocument
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();
    
    [Required]
    [MaxLength(100)]
    [Column("collection")]
    public string Collection { get; set; } = string.Empty;
    
    [Required]
    [MaxLength(500)]
    [Column("title")]
    public string Title { get; set; } = string.Empty;
    
    [Required]
    [Column("content", TypeName = "text")]
    public string Content { get; set; } = string.Empty;
    
    [Column("embedding")]
    public Vector? Embedding { get; set; }
    
    [Column("metadata", TypeName = "jsonb")]
    public Dictionary<string, object> Metadata { get; set; } = new();
    
    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    [Column("updated_at")]
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
