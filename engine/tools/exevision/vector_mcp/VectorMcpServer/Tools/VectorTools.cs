using Microsoft.EntityFrameworkCore;
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Text.Json;
using VectorMcpServer.Configuration;
using VectorMcpServer.Data;
using VectorMcpServer.Models;
using VectorMcpServer.Services;
using Pgvector;
using Pgvector.EntityFrameworkCore;

namespace VectorMcpServer.Tools;

[McpServerToolType]
public class VectorTools
{
    [McpServerTool]
    [Description("Store a document with its embedding in both PostgreSQL and Qdrant")]
    public static async Task<string> StoreDocument(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        IEmbeddingService embeddingService,
        VectorStoreSettings settings,
        [Description("Collection name to store the document")] string collection,
        [Description("Document title")] string title,
        [Description("Document content")] string content,
        [Description("Optional metadata as JSON string")] string? metadata = null)
    {
        try
        {
            var embeddingArray = await embeddingService.GenerateTextEmbeddingAsync(content);
            var embedding = new Vector(embeddingArray);

            var metadataDict = ParseMetadata(metadata);

            var document = new VectorDocument
            {
                Collection = collection,
                Title = title,
                Content = content,
                Embedding = embedding,
                Metadata = metadataDict
            };

            await qdrantService.CreateCollectionAsync(collection, (uint)embeddingArray.Length);

            dbContext.Documents.Add(document);
            await dbContext.SaveChangesAsync();

            var qdrantSuccess = await qdrantService.UpsertPointAsync(collection, document);

            return JsonSerializer.Serialize(new
            {
                success = true,
                document_id = document.Id,
                collection = collection,
                title = title,
                postgres_stored = true,
                qdrant_stored = qdrantSuccess,
                embedding_dimensions = embeddingArray.Length
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("Append analysis for an existing document (stored in a separate analysis collection)")]
    public static async Task<string> AppendAnalysis(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        IEmbeddingService embeddingService,
        VectorStoreSettings settings,
        [Description("Base collection that owns the source document")] string collection,
        [Description("Target document ID")] string documentId,
        [Description("Analysis text to append")] string analysis,
        [Description("Optional analysis collection override")] string? analysisCollection = null,
        [Description("Optional metadata as JSON string")] string? metadata = null)
    {
        try
        {
            if (!Guid.TryParse(documentId, out var docGuid))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Invalid document ID format"
                });
            }

            var exists = await dbContext.Documents.AnyAsync(d => d.Id == docGuid && d.Collection == collection);
            if (!exists)
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Target document not found"
                });
            }

            var targetCollection = string.IsNullOrWhiteSpace(analysisCollection)
                ? $"{collection}__analysis"
                : analysisCollection;

            var metadataDict = ParseMetadata(metadata);
            metadataDict["analysis_of"] = documentId;
            metadataDict["analysis_source_collection"] = collection;

            var embeddingArray = await embeddingService.GenerateTextEmbeddingAsync(analysis);
            var embedding = new Vector(embeddingArray);

            var analysisDocument = new VectorDocument
            {
                Collection = targetCollection,
                Title = $"Analysis for {documentId}",
                Content = analysis,
                Embedding = embedding,
                Metadata = metadataDict
            };

            await qdrantService.CreateCollectionAsync(targetCollection, (uint)embeddingArray.Length);

            dbContext.Documents.Add(analysisDocument);
            await dbContext.SaveChangesAsync();

            var qdrantSuccess = await qdrantService.UpsertPointAsync(targetCollection, analysisDocument);

            return JsonSerializer.Serialize(new
            {
                success = true,
                analysis_document_id = analysisDocument.Id,
                analysis_collection = targetCollection,
                postgres_stored = true,
                qdrant_stored = qdrantSuccess
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("Search for similar documents using vector similarity")]
    public static async Task<string> SearchDocuments(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        IEmbeddingService embeddingService,
        VectorStoreSettings settings,
        [Description("Collection to search in")] string collection,
        [Description("Search query text")] string query,
        [Description("Number of results to return (default: 5)")] int limit = 5,
        [Description("Similarity threshold (0.0 to 1.0, default: 0.7)")] float threshold = 0.7f,
        [Description("Search source: 'postgres', 'qdrant', or 'both' (default: 'both')")] string source = "both",
        [Description("Optional query instruction prefix")] string? queryInstruction = null)
    {
        try
        {
            var queryText = BuildQueryText(query, settings, queryInstruction);
            var queryEmbedding = await embeddingService.GenerateTextEmbeddingAsync(queryText);

            var results = new List<SearchResult>();
            var normalizedSource = string.IsNullOrWhiteSpace(source) ? "both" : source.Trim().ToLowerInvariant();

            if (normalizedSource == "postgres" || normalizedSource == "both")
            {
                var pgVector = new Vector(queryEmbedding);
                var pgResults = await dbContext.Documents
                    .Where(d => d.Collection == collection && d.Embedding != null)
                    .OrderBy(d => d.Embedding!.L2Distance(pgVector))
                    .Take(limit)
                    .Select(d => new SearchResult
                    {
                        Id = d.Id,
                        Title = d.Title,
                        Content = d.Content,
                        Collection = d.Collection,
                        CreatedAt = d.CreatedAt,
                        Metadata = d.Metadata,
                        Source = "postgres",
                        SimilarityScore = 1.0 / (1.0 + d.Embedding!.L2Distance(pgVector))
                    })
                    .ToListAsync();

                results.AddRange(pgResults.Where(r => r.SimilarityScore >= threshold));
            }

            if (normalizedSource == "qdrant" || normalizedSource == "both")
            {
                var qdrantResults = await qdrantService.SearchAsync(collection, queryEmbedding, (uint)limit, threshold);
                var qdrantFormatted = qdrantResults.Select(d => new SearchResult
                {
                    Id = d.Id,
                    Title = d.Title,
                    Content = d.Content,
                    Collection = d.Collection,
                    CreatedAt = d.CreatedAt,
                    Metadata = d.Metadata,
                    Source = "qdrant",
                    SimilarityScore = ReadScore(d.Metadata)
                });

                results.AddRange(qdrantFormatted);
            }

            var finalResults = results
                .OrderByDescending(r => r.SimilarityScore)
                .Take(limit)
                .ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                query = query,
                collection = collection,
                results_count = finalResults.Count,
                search_source = normalizedSource,
                results = finalResults
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("Search across multiple collections. Use '*' to include all collections.")]
    public static async Task<string> SearchAcrossCollections(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        IEmbeddingService embeddingService,
        VectorStoreSettings settings,
        [Description("Comma-separated collections or '*'")] string collections,
        [Description("Search query text")] string query,
        [Description("Number of results to return (default: 5)")] int limit = 5,
        [Description("Similarity threshold (0.0 to 1.0, default: 0.7)")] float threshold = 0.7f,
        [Description("Search source: 'postgres', 'qdrant', or 'both' (default: 'both')")] string source = "both",
        [Description("Optional query instruction prefix")] string? queryInstruction = null)
    {
        try
        {
            var collectionList = await ResolveCollectionsAsync(dbContext, qdrantService, collections);
            if (collectionList.Count == 0)
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "No collections resolved for search"
                });
            }

            var queryText = BuildQueryText(query, settings, queryInstruction);
            var queryEmbedding = await embeddingService.GenerateTextEmbeddingAsync(queryText);

            var results = new List<SearchResult>();
            var normalizedSource = string.IsNullOrWhiteSpace(source) ? "both" : source.Trim().ToLowerInvariant();

            if (normalizedSource == "postgres" || normalizedSource == "both")
            {
                var pgVector = new Vector(queryEmbedding);
                var pgResults = await dbContext.Documents
                    .Where(d => collectionList.Contains(d.Collection) && d.Embedding != null)
                    .OrderBy(d => d.Embedding!.L2Distance(pgVector))
                    .Take(limit)
                    .Select(d => new SearchResult
                    {
                        Id = d.Id,
                        Title = d.Title,
                        Content = d.Content,
                        Collection = d.Collection,
                        CreatedAt = d.CreatedAt,
                        Metadata = d.Metadata,
                        Source = "postgres",
                        SimilarityScore = 1.0 / (1.0 + d.Embedding!.L2Distance(pgVector))
                    })
                    .ToListAsync();

                results.AddRange(pgResults.Where(r => r.SimilarityScore >= threshold));
            }

            if (normalizedSource == "qdrant" || normalizedSource == "both")
            {
                foreach (var collection in collectionList)
                {
                    var qdrantResults = await qdrantService.SearchAsync(collection, queryEmbedding, (uint)limit, threshold);
                    var formatted = qdrantResults.Select(d => new SearchResult
                    {
                        Id = d.Id,
                        Title = d.Title,
                        Content = d.Content,
                        Collection = d.Collection,
                        CreatedAt = d.CreatedAt,
                        Metadata = d.Metadata,
                        Source = "qdrant",
                        SimilarityScore = ReadScore(d.Metadata)
                    });

                    results.AddRange(formatted);
                }
            }

            var finalResults = results
                .OrderByDescending(r => r.SimilarityScore)
                .Take(limit)
                .ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                query = query,
                collections = collectionList,
                results_count = finalResults.Count,
                search_source = normalizedSource,
                results = finalResults
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("List all available collections")]
    public static async Task<string> ListCollections(
        VectorDbContext dbContext,
        IQdrantService qdrantService)
    {
        try
        {
            var pgCollections = await dbContext.Documents
                .Select(d => d.Collection)
                .Distinct()
                .ToListAsync();

            var qdrantCollections = await qdrantService.GetCollectionsAsync();

            var collectionStats = await dbContext.Documents
                .GroupBy(d => d.Collection)
                .Select(g => new
                {
                    collection = g.Key,
                    document_count = g.Count(),
                    latest_update = g.Max(d => d.UpdatedAt)
                })
                .ToListAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                postgres_collections = pgCollections,
                qdrant_collections = qdrantCollections,
                collection_stats = collectionStats
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("Delete a document by ID from both PostgreSQL and Qdrant (requires VECTOR_DELETE_TOKEN)")]
    public static async Task<string> DeleteDocument(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        VectorStoreSettings settings,
        [Description("Document ID to delete")] string documentId,
        [Description("Collection name")] string collection,
        [Description("Admin delete token")] string adminToken)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(settings.DeleteToken))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Delete is disabled. Set VECTOR_DELETE_TOKEN to enable."
                });
            }

            if (!string.Equals(settings.DeleteToken, adminToken, StringComparison.Ordinal))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Invalid delete token"
                });
            }

            if (!Guid.TryParse(documentId, out var docGuid))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Invalid document ID format"
                });
            }

            var document = await dbContext.Documents
                .FirstOrDefaultAsync(d => d.Id == docGuid && d.Collection == collection);

            var pgDeleted = false;
            if (document != null)
            {
                dbContext.Documents.Remove(document);
                await dbContext.SaveChangesAsync();
                pgDeleted = true;
            }

            var qdrantDeleted = await qdrantService.DeletePointAsync(collection, docGuid);

            return JsonSerializer.Serialize(new
            {
                success = pgDeleted || qdrantDeleted,
                document_id = documentId,
                collection = collection,
                postgres_deleted = pgDeleted,
                qdrant_deleted = qdrantDeleted
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    [McpServerTool]
    [Description("Get document details by ID")]
    public static async Task<string> GetDocument(
        VectorDbContext dbContext,
        [Description("Document ID")] string documentId)
    {
        try
        {
            if (!Guid.TryParse(documentId, out var docGuid))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Invalid document ID format"
                });
            }

            var document = await dbContext.Documents
                .FirstOrDefaultAsync(d => d.Id == docGuid);

            if (document == null)
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Document not found"
                });
            }

            return JsonSerializer.Serialize(new
            {
                success = true,
                document = new
                {
                    id = document.Id,
                    collection = document.Collection,
                    title = document.Title,
                    content = document.Content,
                    metadata = document.Metadata,
                    created_at = document.CreatedAt,
                    updated_at = document.UpdatedAt,
                    has_embedding = document.Embedding != null
                }
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error = ex.Message
            });
        }
    }

    private static Dictionary<string, object> ParseMetadata(string? metadata)
    {
        var metadataDict = new Dictionary<string, object>();
        if (string.IsNullOrWhiteSpace(metadata))
        {
            return metadataDict;
        }

        try
        {
            var jsonDoc = JsonDocument.Parse(metadata);
            foreach (var prop in jsonDoc.RootElement.EnumerateObject())
            {
                metadataDict[prop.Name] = prop.Value.ToString();
            }
        }
        catch (JsonException)
        {
            metadataDict["metadata_error"] = "Invalid JSON format";
        }

        return metadataDict;
    }

    private static string BuildQueryText(string query, VectorStoreSettings settings, string? queryInstruction)
    {
        var instruction = string.IsNullOrWhiteSpace(queryInstruction)
            ? settings.EmbeddingQueryPrefix
            : queryInstruction;

        if (string.IsNullOrWhiteSpace(instruction))
        {
            return query;
        }

        return $"{instruction}\nQuery:{query}";
    }

    private static async Task<List<string>> ResolveCollectionsAsync(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        string collections)
    {
        if (string.IsNullOrWhiteSpace(collections) || collections.Trim() == "*")
        {
            var pgCollections = await dbContext.Documents
                .Select(d => d.Collection)
                .Distinct()
                .ToListAsync();

            var qdrantCollections = await qdrantService.GetCollectionsAsync();

            return pgCollections
                .Concat(qdrantCollections)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        return collections
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static double ReadScore(Dictionary<string, object> metadata)
    {
        if (metadata.TryGetValue("score", out var value) && value != null)
        {
            if (double.TryParse(value.ToString(), out var parsed))
            {
                return parsed;
            }
        }

        return 0.0;
    }

    private sealed class SearchResult
    {
        public Guid Id { get; init; }
        public string Title { get; init; } = string.Empty;
        public string Content { get; init; } = string.Empty;
        public string Collection { get; init; } = string.Empty;
        public DateTime CreatedAt { get; init; }
        public Dictionary<string, object> Metadata { get; init; } = new();
        public string Source { get; init; } = string.Empty;
        public double SimilarityScore { get; init; }
    }
}
