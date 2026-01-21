using Microsoft.EntityFrameworkCore;
using VectorMcpServer.Models;
using Pgvector.EntityFrameworkCore;
using VectorMcpServer.Configuration;

namespace VectorMcpServer.Data;

public class VectorDbContext : DbContext
{
    private readonly int _embeddingDimension;

    public VectorDbContext(DbContextOptions<VectorDbContext> options, VectorStoreSettings settings) : base(options)
    {
        _embeddingDimension = settings.EmbeddingDimension;
    }

    public DbSet<VectorDocument> Documents { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Configure pgvector extension
        modelBuilder.HasPostgresExtension("vector");

        modelBuilder.Entity<VectorDocument>(entity =>
        {
            entity.ToTable("vector_documents");
            
            entity.Property(e => e.Id)
                .HasColumnName("id");
            
            entity.Property(e => e.Collection)
                .HasColumnName("collection")
                .HasMaxLength(100);
            
            entity.Property(e => e.Title)
                .HasColumnName("title")
                .HasMaxLength(500);
            
            entity.Property(e => e.Content)
                .HasColumnName("content")
                .HasColumnType("text");
            
            var vectorColumnType = $"vector({_embeddingDimension})";
            entity.Property(e => e.Embedding)
                .HasColumnName("embedding")
                .HasColumnType(vectorColumnType);
            
            entity.Property(e => e.Metadata)
                .HasColumnName("metadata")
                .HasColumnType("jsonb");
            
            entity.Property(e => e.CreatedAt)
                .HasColumnName("created_at");
            
            entity.Property(e => e.UpdatedAt)
                .HasColumnName("updated_at");

            // Indexes
            entity.HasIndex(e => e.Collection);
            entity.HasIndex(e => e.Embedding)
                .HasMethod("ivfflat")
                .HasOperators("vector_cosine_ops");
        });
    }
}
