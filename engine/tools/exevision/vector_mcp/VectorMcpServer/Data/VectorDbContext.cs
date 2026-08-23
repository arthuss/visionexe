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
    public DbSet<RunRecord> Runs { get; set; }
    public DbSet<ArtifactRecord> Artifacts { get; set; }
    public DbSet<RunOutput> RunOutputs { get; set; }
    public DbSet<TextUnit> TextUnits { get; set; }
    public DbSet<AnalysisArtifact> AnalysisArtifacts { get; set; }
    public DbSet<AssetSet> AssetSets { get; set; }
    public DbSet<AssetSetItem> AssetSetItems { get; set; }
    public DbSet<SubjectRecord> Subjects { get; set; }
    public DbSet<SubjectOccurrence> SubjectOccurrences { get; set; }
    public DbSet<SubjectAssetLink> SubjectAssetLinks { get; set; }
    public DbSet<LayerLink> LayerLinks { get; set; }
    public DbSet<EngramIndexEntry> EngramIndexEntries { get; set; }

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

        modelBuilder.Entity<RunRecord>(entity =>
        {
            entity.ToTable("runs");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.RunType).HasColumnName("run_type").HasColumnType("text");
            entity.Property(e => e.StoryId).HasColumnName("story_id").HasColumnType("text");
            entity.Property(e => e.TimelineId).HasColumnName("timeline_id").HasColumnType("text");
            entity.Property(e => e.UnitRef).HasColumnName("unit_ref").HasColumnType("text");
            entity.Property(e => e.InputSha256).HasColumnName("input_sha256").HasColumnType("text");
            entity.Property(e => e.PromptBundleSha).HasColumnName("prompt_bundle_sha").HasColumnType("text");
            entity.Property(e => e.ModelId).HasColumnName("model_id").HasColumnType("text");
            entity.Property(e => e.Settings).HasColumnName("settings").HasColumnType("jsonb");
            entity.Property(e => e.Inputs).HasColumnName("inputs").HasColumnType("jsonb");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.RunType);
            entity.HasIndex(e => e.StoryId);
            entity.HasIndex(e => e.TimelineId);
            entity.HasIndex(e => e.UnitRef);
        });

        modelBuilder.Entity<ArtifactRecord>(entity =>
        {
            entity.ToTable("artifacts");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.Kind).HasColumnName("kind").HasColumnType("text");
            entity.Property(e => e.Sha256).HasColumnName("sha256").HasColumnType("text");
            entity.Property(e => e.Content).HasColumnName("content").HasColumnType("text");
            entity.Property(e => e.StoragePath).HasColumnName("storage_path").HasColumnType("text");
            entity.Property(e => e.Mime).HasColumnName("mime").HasColumnType("text");
            entity.Property(e => e.SizeBytes).HasColumnName("size_bytes");
            entity.Property(e => e.RunId).HasColumnName("run_id");
            entity.Property(e => e.StoryId).HasColumnName("story_id").HasColumnType("text");
            entity.Property(e => e.TimelineId).HasColumnName("timeline_id").HasColumnType("text");
            entity.Property(e => e.UnitRef).HasColumnName("unit_ref").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.Kind);
            entity.HasIndex(e => e.Sha256);
            entity.HasIndex(e => e.StoryId);
            entity.HasIndex(e => e.TimelineId);
            entity.HasIndex(e => e.UnitRef);
        });

        modelBuilder.Entity<RunOutput>(entity =>
        {
            entity.ToTable("run_outputs");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.RunId).HasColumnName("run_id");
            entity.Property(e => e.ArtifactId).HasColumnName("artifact_id");
            entity.Property(e => e.Role).HasColumnName("role").HasColumnType("text");
            entity.Property(e => e.Ordinal).HasColumnName("ordinal");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.RunId);
            entity.HasIndex(e => e.ArtifactId);
        });

        modelBuilder.Entity<TextUnit>(entity =>
        {
            entity.ToTable("text_units");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.UnitRef).HasColumnName("unit_ref").HasColumnType("text");
            entity.Property(e => e.StoryId).HasColumnName("story_id").HasColumnType("text");
            entity.Property(e => e.TimelineId).HasColumnName("timeline_id").HasColumnType("text");
            entity.Property(e => e.ChapterId).HasColumnName("chapter_id").HasColumnType("text");
            entity.Property(e => e.SegmentLabel).HasColumnName("segment_label").HasColumnType("text");
            entity.Property(e => e.SegmentType).HasColumnName("segment_type").HasColumnType("text");
            entity.Property(e => e.VerseId).HasColumnName("verse_id").HasColumnType("text");
            entity.Property(e => e.SceneId).HasColumnName("scene_id").HasColumnType("text");
            entity.Property(e => e.Content).HasColumnName("content").HasColumnType("text");
            entity.Property(e => e.Sha256).HasColumnName("sha256").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.UnitRef);
            entity.HasIndex(e => e.StoryId);
            entity.HasIndex(e => e.TimelineId);
            entity.HasIndex(e => e.ChapterId);
            entity.HasIndex(e => e.SegmentLabel);
            entity.HasIndex(e => e.SceneId);
        });

        modelBuilder.Entity<AnalysisArtifact>(entity =>
        {
            entity.ToTable("analysis_artifacts");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.TextUnitId).HasColumnName("text_unit_id");
            entity.Property(e => e.AnalysisType).HasColumnName("analysis_type").HasColumnType("text");
            entity.Property(e => e.ArtifactId).HasColumnName("artifact_id");
            entity.Property(e => e.Content).HasColumnName("content").HasColumnType("text");
            entity.Property(e => e.Sha256).HasColumnName("sha256").HasColumnType("text");
            entity.Property(e => e.PromptBundleSha).HasColumnName("prompt_bundle_sha").HasColumnType("text");
            entity.Property(e => e.ModelId).HasColumnName("model_id").HasColumnType("text");
            entity.Property(e => e.Settings).HasColumnName("settings").HasColumnType("jsonb");
            entity.Property(e => e.RunId).HasColumnName("run_id");
            entity.Property(e => e.SupersedesId).HasColumnName("supersedes_id");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.TextUnitId);
            entity.HasIndex(e => e.AnalysisType);
            entity.HasIndex(e => e.RunId);
        });

        modelBuilder.Entity<AssetSet>(entity =>
        {
            entity.ToTable("asset_sets");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.StoryId).HasColumnName("story_id").HasColumnType("text");
            entity.Property(e => e.TimelineId).HasColumnName("timeline_id").HasColumnType("text");
            entity.Property(e => e.ChapterId).HasColumnName("chapter_id").HasColumnType("text");
            entity.Property(e => e.SegmentLabel).HasColumnName("segment_label").HasColumnType("text");
            entity.Property(e => e.SubjectId).HasColumnName("subject_id").HasColumnType("text");
            entity.Property(e => e.SceneId).HasColumnName("scene_id").HasColumnType("text");
            entity.Property(e => e.Label).HasColumnName("label").HasColumnType("text");
            entity.Property(e => e.SetType).HasColumnName("set_type").HasColumnType("text");
            entity.Property(e => e.Variant).HasColumnName("variant").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.StoryId);
            entity.HasIndex(e => e.TimelineId);
            entity.HasIndex(e => e.SubjectId);
            entity.HasIndex(e => e.SceneId);
        });

        modelBuilder.Entity<AssetSetItem>(entity =>
        {
            entity.ToTable("asset_set_items");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.SetId).HasColumnName("set_id");
            entity.Property(e => e.ArtifactId).HasColumnName("artifact_id");
            entity.Property(e => e.Role).HasColumnName("role").HasColumnType("text");
            entity.Property(e => e.Ordinal).HasColumnName("ordinal");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.SetId);
            entity.HasIndex(e => e.ArtifactId);
        });

        modelBuilder.Entity<SubjectRecord>(entity =>
        {
            entity.ToTable("subjects");
            entity.Property(e => e.Id).HasColumnName("id").HasColumnType("text");
            entity.Property(e => e.Name).HasColumnName("name").HasColumnType("text");
            entity.Property(e => e.SubjectType).HasColumnName("subject_type").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.SubjectType);
            entity.HasIndex(e => e.Name);
        });

        modelBuilder.Entity<SubjectOccurrence>(entity =>
        {
            entity.ToTable("subject_occurrences");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.SubjectId).HasColumnName("subject_id").HasColumnType("text");
            entity.Property(e => e.SourceId).HasColumnName("source_id").HasColumnType("text");
            entity.Property(e => e.Chapter).HasColumnName("chapter").HasColumnType("text");
            entity.Property(e => e.SegmentLabel).HasColumnName("segment_label").HasColumnType("text");
            entity.Property(e => e.SegmentType).HasColumnName("segment_type").HasColumnType("text");
            entity.Property(e => e.PhaseId).HasColumnName("phase_id").HasColumnType("text");
            entity.Property(e => e.SceneLabel).HasColumnName("scene_label").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.SubjectId);
            entity.HasIndex(e => e.Chapter);
            entity.HasIndex(e => e.PhaseId);
        });

        modelBuilder.Entity<SubjectAssetLink>(entity =>
        {
            entity.ToTable("subject_asset_links");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.SubjectId).HasColumnName("subject_id").HasColumnType("text");
            entity.Property(e => e.SetId).HasColumnName("set_id");
            entity.Property(e => e.Variant).HasColumnName("variant").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.SubjectId);
            entity.HasIndex(e => e.SetId);
        });

        modelBuilder.Entity<LayerLink>(entity =>
        {
            entity.ToTable("layer_links");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.OwnerKind).HasColumnName("owner_kind").HasColumnType("text");
            entity.Property(e => e.OwnerId).HasColumnName("owner_id").HasColumnType("text");
            entity.Property(e => e.SetId).HasColumnName("set_id");
            entity.Property(e => e.LayerType).HasColumnName("layer_type").HasColumnType("text");
            entity.Property(e => e.Role).HasColumnName("role").HasColumnType("text");
            entity.Property(e => e.Scope).HasColumnName("scope").HasColumnType("text");
            entity.Property(e => e.Metadata).HasColumnName("meta").HasColumnType("jsonb");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.OwnerKind);
            entity.HasIndex(e => e.OwnerId);
            entity.HasIndex(e => e.SetId);
        });

        modelBuilder.Entity<EngramIndexEntry>(entity =>
        {
            entity.ToTable("engram_index");
            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.DocumentId).HasColumnName("document_id");
            entity.Property(e => e.Collection).HasColumnName("collection").HasColumnType("text");
            entity.Property(e => e.LayerId).HasColumnName("layer_id");
            entity.Property(e => e.Hashes).HasColumnName("hashes").HasColumnType("bigint[]");
            entity.Property(e => e.TokenCount).HasColumnName("token_count");
            entity.Property(e => e.CreatedAt).HasColumnName("created_at");
            entity.HasIndex(e => e.DocumentId);
            entity.HasIndex(e => e.Collection);
            entity.HasIndex(e => e.LayerId);
        });
    }
}
