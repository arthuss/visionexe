using Microsoft.EntityFrameworkCore;
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Data;
using System.Net.Http;
using System.Text.Json;
using Npgsql;
using NpgsqlTypes;
using VectorMcpServer.Configuration;
using VectorMcpServer.Data;
using VectorMcpServer.Models;
using VectorMcpServer.Services;
using VectorMcpServer.Services.Engram;
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
        IEngramIndexer engramIndexer,
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
            var engramIndexed = false;
            var engramLayers = 0;
            var engramTokens = 0;
            string? engramError = null;

            if (engramIndexer.IsEnabled)
            {
                try
                {
                    var hashResult = engramIndexer.ComputeHashes(content);
                    if (hashResult != null && hashResult.LayerHashes.Count > 0)
                    {
                        foreach (var layer in hashResult.LayerHashes)
                        {
                            dbContext.EngramIndexEntries.Add(new EngramIndexEntry
                            {
                                DocumentId = document.Id,
                                Collection = collection,
                                LayerId = layer.Key,
                                Hashes = layer.Value,
                                TokenCount = hashResult.TokenCount
                            });
                        }

                        await dbContext.SaveChangesAsync();
                        engramIndexed = true;
                        engramLayers = hashResult.LayerHashes.Count;
                        engramTokens = hashResult.TokenCount;
                    }
                }
                catch (Exception ex)
                {
                    engramError = ex.Message;
                }
            }

            return JsonSerializer.Serialize(new
            {
                success = true,
                document_id = document.Id,
                collection = collection,
                title = title,
                postgres_stored = true,
                qdrant_stored = qdrantSuccess,
                embedding_dimensions = embeddingArray.Length,
                engram_indexed = engramIndexed,
                engram_layers = engramLayers,
                engram_token_count = engramTokens,
                engram_error = engramError
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
    [Description("Get a document by collection and title")]
    public static async Task<string> GetDocumentByTitle(
        VectorDbContext dbContext,
        [Description("Collection name")] string collection,
        [Description("Document title")] string title)
    {
        try
        {
            var document = await dbContext.Documents
                .AsNoTracking()
                .FirstOrDefaultAsync(d => d.Collection == collection && d.Title == title);

            if (document == null)
            {
                return JsonSerializer.Serialize(new
                {
                    success = true,
                    found = false
                });
            }

            return JsonSerializer.Serialize(new
            {
                success = true,
                found = true,
                document_id = document.Id,
                collection = document.Collection,
                title = document.Title,
                metadata = document.Metadata,
                created_at = document.CreatedAt,
                updated_at = document.UpdatedAt
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
    [Description("Delete a document by collection and title (Postgres + Qdrant + Engram index)")]
    public static async Task<string> DeleteDocumentByTitle(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        [Description("Collection name")] string collection,
        [Description("Document title")] string title)
    {
        try
        {
            var document = await dbContext.Documents
                .FirstOrDefaultAsync(d => d.Collection == collection && d.Title == title);

            if (document == null)
            {
                return JsonSerializer.Serialize(new
                {
                    success = true,
                    found = false
                });
            }

            var engramEntries = dbContext.EngramIndexEntries
                .Where(e => e.DocumentId == document.Id);
            dbContext.EngramIndexEntries.RemoveRange(engramEntries);
            dbContext.Documents.Remove(document);
            await dbContext.SaveChangesAsync();

            var qdrantSuccess = await qdrantService.DeletePointAsync(document.Collection, document.Id);

            return JsonSerializer.Serialize(new
            {
                success = true,
                found = true,
                document_id = document.Id,
                collection = document.Collection,
                qdrant_deleted = qdrantSuccess
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
                }).ToList();

                if (UseMinimalQdrantPayload(settings))
                {
                    qdrantFormatted = await HydrateFromPostgresAsync(dbContext, qdrantFormatted);
                }

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
                    }).ToList();

                    if (UseMinimalQdrantPayload(settings))
                    {
                        formatted = await HydrateFromPostgresAsync(dbContext, formatted);
                    }

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
    [Description("Search Qdrant with a raw filter JSON payload")]
    public static async Task<string> SearchDocumentsWithFilter(
        VectorDbContext dbContext,
        IEmbeddingService embeddingService,
        VectorStoreSettings settings,
        [Description("Collection to search in")] string collection,
        [Description("Search query text")] string query,
        [Description("Qdrant filter JSON string")] string filterJson,
        [Description("Number of results to return (default: 5)")] int limit = 5,
        [Description("Similarity threshold (0.0 to 1.0, default: 0.7)")] float threshold = 0.7f,
        [Description("Optional query instruction prefix")] string? queryInstruction = null,
        [Description("Optional HNSW ef (higher recall)")] int? hnswEf = null,
        [Description("Exact search (slower, deterministic)")] bool exact = false)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(filterJson))
            {
                return JsonSerializer.Serialize(new { success = false, error = "filterJson is required" });
            }

            JsonDocument filterDoc;
            try
            {
                filterDoc = JsonDocument.Parse(filterJson);
            }
            catch (JsonException)
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid filter JSON" });
            }

            var queryText = BuildQueryText(query, settings, queryInstruction);
            var queryEmbedding = await embeddingService.GenerateTextEmbeddingAsync(queryText);

            var payload = new Dictionary<string, object>
            {
                ["vector"] = queryEmbedding,
                ["limit"] = limit,
                ["score_threshold"] = threshold,
                ["with_payload"] = true,
                ["filter"] = filterDoc.RootElement
            };

            if (hnswEf.HasValue || exact)
            {
                var searchParams = new Dictionary<string, object>();
                if (hnswEf.HasValue)
                {
                    searchParams["hnsw_ef"] = hnswEf.Value;
                }

                if (exact)
                {
                    searchParams["exact"] = true;
                }

                payload["params"] = searchParams;
            }

            var qdrantUrl = $"http://{settings.QdrantHost}:{settings.QdrantHttpPort}/collections/{collection}/points/search";

            using var http = new HttpClient();
            var requestBody = JsonSerializer.Serialize(payload);
            using var response = await http.PostAsync(qdrantUrl, new StringContent(requestBody, System.Text.Encoding.UTF8, "application/json"));
            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return JsonSerializer.Serialize(new { success = false, error = responseBody });
            }

            var results = new List<SearchResult>();
            using (var doc = JsonDocument.Parse(responseBody))
            {
                if (doc.RootElement.TryGetProperty("result", out var resultArray) && resultArray.ValueKind == JsonValueKind.Array)
                {
                    foreach (var item in resultArray.EnumerateArray())
                    {
                        var payloadElement = item.TryGetProperty("payload", out var payloadValue) ? payloadValue : default;
                        var title = payloadElement.ValueKind == JsonValueKind.Object && payloadElement.TryGetProperty("title", out var titleValue)
                            ? titleValue.GetString() ?? string.Empty
                            : string.Empty;
                        var content = payloadElement.ValueKind == JsonValueKind.Object && payloadElement.TryGetProperty("content", out var contentValue)
                            ? contentValue.GetString() ?? string.Empty
                            : string.Empty;
                        var collectionName = payloadElement.ValueKind == JsonValueKind.Object && payloadElement.TryGetProperty("collection", out var collectionValue)
                            ? collectionValue.GetString() ?? collection
                            : collection;
                        var createdAt = DateTime.UtcNow;
                        if (payloadElement.ValueKind == JsonValueKind.Object && payloadElement.TryGetProperty("created_at", out var createdValue))
                        {
                            DateTime.TryParse(createdValue.GetString(), out createdAt);
                        }

                        var metadata = new Dictionary<string, object>();
                        if (payloadElement.ValueKind == JsonValueKind.Object)
                        {
                            foreach (var prop in payloadElement.EnumerateObject())
                            {
                                metadata[prop.Name] = prop.Value.ToString();
                            }
                        }

                        var score = item.TryGetProperty("score", out var scoreValue) ? scoreValue.GetDouble() : 0.0;
                        var id = item.TryGetProperty("id", out var idValue) && Guid.TryParse(idValue.ToString(), out var parsedId)
                            ? parsedId
                            : Guid.Empty;

                        results.Add(new SearchResult
                        {
                            Id = id,
                            Title = title,
                            Content = content,
                            Collection = collectionName,
                            CreatedAt = createdAt,
                            Metadata = metadata,
                            Source = "qdrant",
                            SimilarityScore = score
                        });
                    }
                }
            }

            if (UseMinimalQdrantPayload(settings))
            {
                results = await HydrateFromPostgresAsync(dbContext, results);
            }

            var finalResults = results
                .OrderByDescending(r => r.SimilarityScore)
                .Take(limit)
                .ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                query,
                collection,
                results_count = finalResults.Count,
                results = finalResults
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new { success = false, error = ex.Message });
        }
    }

    [McpServerTool]
    [Description("Resolve documents via Engram hash overlap (engram_index -> document_id) with linked pgvector/Qdrant IDs")]
    public static async Task<string> EngramLookup(
        VectorDbContext dbContext,
        IEngramIndexer engramIndexer,
        [Description("Query text for Engram hashing")] string query,
        [Description("Comma-separated collections or '*' (default: '*')")] string collections = "*",
        [Description("Maximum results to return (default: 20)")] int limit = 20,
        [Description("Minimum shared hashes across all layers (default: 1)")] int minSharedHashes = 1,
        [Description("Include full document content in results (default: false)")] bool includeContent = false)
    {
        try
        {
            if (!engramIndexer.IsEnabled)
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "Engram indexer is disabled. Configure ENGRAM_PARAMS_PATH and ENGRAM_TOKENIZER_DIR."
                });
            }

            if (string.IsNullOrWhiteSpace(query))
            {
                return JsonSerializer.Serialize(new
                {
                    success = false,
                    error = "query is required"
                });
            }

            limit = Math.Clamp(limit, 1, 500);
            minSharedHashes = Math.Max(1, minSharedHashes);

            var hashResult = engramIndexer.ComputeHashes(query);
            if (hashResult == null || hashResult.LayerHashes.Count == 0)
            {
                return JsonSerializer.Serialize(new
                {
                    success = true,
                    query,
                    results_count = 0,
                    results = Array.Empty<object>()
                });
            }

            var collectionFilter = ParseCollectionFilter(collections);
            var useCollectionFilter = collectionFilter.Count > 0;
            var aggregateByDocument = new Dictionary<Guid, EngramAggregate>();

            var connection = dbContext.Database.GetDbConnection();
            var shouldCloseConnection = connection.State != ConnectionState.Open;
            if (shouldCloseConnection)
            {
                await connection.OpenAsync();
            }

            try
            {
                foreach (var layer in hashResult.LayerHashes)
                {
                    var layerHashes = layer.Value?
                        .Distinct()
                        .ToArray() ?? Array.Empty<long>();

                    if (layerHashes.Length == 0)
                    {
                        continue;
                    }

                    var layerHashSet = layerHashes.ToHashSet();

                    await using var command = connection.CreateCommand();
                    command.CommandText = useCollectionFilter
                        ? "SELECT document_id, collection, token_count, hashes " +
                          "FROM engram_index " +
                          "WHERE layer_id = @layer_id AND hashes && @query_hashes AND collection = ANY(@collections)"
                        : "SELECT document_id, collection, token_count, hashes " +
                          "FROM engram_index " +
                          "WHERE layer_id = @layer_id AND hashes && @query_hashes";

                    command.Parameters.Add(new NpgsqlParameter("layer_id", layer.Key));
                    command.Parameters.Add(new NpgsqlParameter("query_hashes", NpgsqlDbType.Array | NpgsqlDbType.Bigint)
                    {
                        Value = layerHashes
                    });

                    if (useCollectionFilter)
                    {
                        command.Parameters.Add(new NpgsqlParameter("collections", NpgsqlDbType.Array | NpgsqlDbType.Text)
                        {
                            Value = collectionFilter.ToArray()
                        });
                    }

                    await using var reader = await command.ExecuteReaderAsync();
                    while (await reader.ReadAsync())
                    {
                        var documentId = reader.GetGuid(0);
                        var collectionName = reader.IsDBNull(1) ? string.Empty : reader.GetString(1);
                        var tokenCount = reader.IsDBNull(2) ? 0 : reader.GetInt32(2);
                        var entryHashes = reader.IsDBNull(3) ? Array.Empty<long>() : reader.GetFieldValue<long[]>(3);

                        var sharedCount = 0;
                        foreach (var hash in entryHashes)
                        {
                            if (layerHashSet.Contains(hash))
                            {
                                sharedCount++;
                            }
                        }

                        if (sharedCount <= 0)
                        {
                            continue;
                        }

                        if (!aggregateByDocument.TryGetValue(documentId, out var aggregate))
                        {
                            aggregate = new EngramAggregate
                            {
                                DocumentId = documentId,
                                Collection = collectionName,
                                TokenCount = tokenCount
                            };
                            aggregateByDocument[documentId] = aggregate;
                        }

                        if (string.IsNullOrWhiteSpace(aggregate.Collection) && !string.IsNullOrWhiteSpace(collectionName))
                        {
                            aggregate.Collection = collectionName;
                        }

                        aggregate.TokenCount = Math.Max(aggregate.TokenCount, tokenCount);
                        aggregate.SharedHashes += sharedCount;
                        aggregate.MatchedLayers.Add(layer.Key);
                        aggregate.LayerHits[layer.Key] = aggregate.LayerHits.TryGetValue(layer.Key, out var existing)
                            ? existing + sharedCount
                            : sharedCount;
                    }
                }
            }
            finally
            {
                if (shouldCloseConnection)
                {
                    await connection.CloseAsync();
                }
            }

            var totalQueryHashes = hashResult.LayerHashes.Sum(layer => layer.Value?.Length ?? 0);

            var candidates = aggregateByDocument.Values
                .Where(c => c.SharedHashes >= minSharedHashes)
                .OrderByDescending(c => c.MatchedLayers.Count)
                .ThenByDescending(c => c.SharedHashes)
                .Take(limit)
                .ToList();

            if (candidates.Count == 0)
            {
                return JsonSerializer.Serialize(new
                {
                    success = true,
                    query,
                    collection_filter = useCollectionFilter ? collectionFilter.ToArray() : new[] { "*" },
                    total_query_tokens = hashResult.TokenCount,
                    query_hashes_by_layer = hashResult.LayerHashes.ToDictionary(k => k.Key.ToString(), v => v.Value.Length),
                    total_query_hashes = totalQueryHashes,
                    min_shared_hashes = minSharedHashes,
                    results_count = 0,
                    results = Array.Empty<object>()
                });
            }

            var candidateIds = candidates
                .Select(c => c.DocumentId)
                .Distinct()
                .ToList();

            var documents = await dbContext.Documents
                .AsNoTracking()
                .Where(d => candidateIds.Contains(d.Id))
                .ToListAsync();

            var documentMap = documents.ToDictionary(d => d.Id);
            var results = new List<object>(candidates.Count);

            foreach (var candidate in candidates)
            {
                documentMap.TryGetValue(candidate.DocumentId, out var document);
                var resolvedCollection = !string.IsNullOrWhiteSpace(candidate.Collection)
                    ? candidate.Collection
                    : document?.Collection ?? string.Empty;

                var score = totalQueryHashes > 0
                    ? (double)candidate.SharedHashes / totalQueryHashes
                    : 0.0d;

                var metadata = document?.Metadata ?? new Dictionary<string, object>();
                var layerHitCounts = candidate.LayerHits
                    .OrderBy(k => k.Key)
                    .ToDictionary(
                        keySelector: item => item.Key.ToString(),
                        elementSelector: item => item.Value);

                results.Add(new
                {
                    document_id = candidate.DocumentId,
                    collection = resolvedCollection,
                    title = document?.Title ?? string.Empty,
                    content = includeContent ? document?.Content ?? string.Empty : string.Empty,
                    metadata,
                    token_count = candidate.TokenCount,
                    matched_layers = candidate.MatchedLayers.OrderBy(v => v).ToArray(),
                    matched_layer_count = candidate.MatchedLayers.Count,
                    shared_hash_count = candidate.SharedHashes,
                    layer_hit_counts = layerHitCounts,
                    engram_score = score,
                    qdrant_ref = new
                    {
                        collection = resolvedCollection,
                        point_id = candidate.DocumentId.ToString()
                    }
                });
            }

            return JsonSerializer.Serialize(new
            {
                success = true,
                query,
                collection_filter = useCollectionFilter ? collectionFilter.ToArray() : new[] { "*" },
                total_query_tokens = hashResult.TokenCount,
                query_hashes_by_layer = hashResult.LayerHashes.ToDictionary(k => k.Key.ToString(), v => v.Value.Length),
                total_query_hashes = totalQueryHashes,
                min_shared_hashes = minSharedHashes,
                results_count = results.Count,
                results
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
    [Description("Scroll Qdrant points using a raw filter JSON payload (exact match, no vector search)")]
    public static async Task<string> ScrollPointsWithFilter(
        VectorStoreSettings settings,
        [Description("Collection to scroll")] string collection,
        [Description("Qdrant filter JSON string")] string filterJson,
        [Description("Number of points to return (default: 100)")] int limit = 100,
        [Description("Optional offset JSON string from prior next_page_offset")] string? offsetJson = null,
        [Description("Include payloads (default: true)")] bool withPayload = true,
        [Description("Include vectors (default: false)")] bool withVectors = false)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(filterJson))
            {
                return JsonSerializer.Serialize(new { success = false, error = "filterJson is required" });
            }

            JsonDocument filterDoc;
            try
            {
                filterDoc = JsonDocument.Parse(filterJson);
            }
            catch (JsonException)
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid filter JSON" });
            }

            JsonDocument? offsetDoc = null;
            if (!string.IsNullOrWhiteSpace(offsetJson))
            {
                try
                {
                    offsetDoc = JsonDocument.Parse(offsetJson);
                }
                catch (JsonException)
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid offset JSON" });
                }
            }

            var payload = new Dictionary<string, object>
            {
                ["limit"] = limit,
                ["with_payload"] = withPayload,
                ["with_vectors"] = withVectors,
                ["filter"] = filterDoc.RootElement
            };

            if (offsetDoc != null)
            {
                payload["offset"] = offsetDoc.RootElement;
            }

            var qdrantUrl = $"http://{settings.QdrantHost}:{settings.QdrantHttpPort}/collections/{collection}/points/scroll";

            using var http = new HttpClient();
            var requestBody = JsonSerializer.Serialize(payload);
            using var response = await http.PostAsync(qdrantUrl, new StringContent(requestBody, System.Text.Encoding.UTF8, "application/json"));
            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                return JsonSerializer.Serialize(new { success = false, error = responseBody });
            }

            var points = new List<Dictionary<string, object>>();
            string? nextOffset = null;

            using (var doc = JsonDocument.Parse(responseBody))
            {
                if (doc.RootElement.TryGetProperty("result", out var resultElement))
                {
                    if (resultElement.TryGetProperty("next_page_offset", out var offsetElement))
                    {
                        nextOffset = offsetElement.GetRawText();
                    }

                    if (resultElement.TryGetProperty("points", out var pointsArray) && pointsArray.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var item in pointsArray.EnumerateArray())
                        {
                            var point = new Dictionary<string, object>();

                            if (item.TryGetProperty("id", out var idValue))
                            {
                                point["id"] = idValue.ToString();
                            }

                            if (item.TryGetProperty("payload", out var payloadValue))
                            {
                                var parsedPayload = JsonSerializer.Deserialize<Dictionary<string, object>>(payloadValue.GetRawText());
                                point["payload"] = parsedPayload ?? new Dictionary<string, object>();
                            }

                            if (withVectors && item.TryGetProperty("vector", out var vectorValue))
                            {
                                var parsedVector = JsonSerializer.Deserialize<object>(vectorValue.GetRawText());
                                point["vector"] = parsedVector ?? vectorValue.GetRawText();
                            }

                            points.Add(point);
                        }
                    }
                }
            }

            return JsonSerializer.Serialize(new
            {
                success = true,
                collection,
                results_count = points.Count,
                next_page_offset = nextOffset,
                points
            });
        }
        catch (Exception ex)
        {
            return JsonSerializer.Serialize(new { success = false, error = ex.Message });
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

    private static bool UseMinimalQdrantPayload(VectorStoreSettings settings)
    {
        return string.Equals(settings.QdrantPayloadMode, "minimal", StringComparison.OrdinalIgnoreCase);
    }

    private static List<string> ParseCollectionFilter(string? collections)
    {
        if (string.IsNullOrWhiteSpace(collections))
        {
            return new List<string>();
        }

        if (collections.Trim() == "*")
        {
            return new List<string>();
        }

        return collections
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Where(collection => collection != "*")
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static async Task<List<SearchResult>> HydrateFromPostgresAsync(
        VectorDbContext dbContext,
        List<SearchResult> results)
    {
        var missingIds = results
            .Where(r => string.IsNullOrWhiteSpace(r.Content))
            .Select(r => r.Id)
            .Distinct()
            .ToList();

        if (missingIds.Count == 0)
        {
            return results;
        }

        var documents = await dbContext.Documents
            .AsNoTracking()
            .Where(d => missingIds.Contains(d.Id))
            .ToListAsync();

        var documentMap = documents.ToDictionary(d => d.Id);
        var hydrated = new List<SearchResult>(results.Count);

        foreach (var result in results)
        {
            if (!documentMap.TryGetValue(result.Id, out var doc))
            {
                hydrated.Add(result);
                continue;
            }

            var metadata = new Dictionary<string, object>(doc.Metadata ?? new Dictionary<string, object>())
            {
                ["score"] = result.SimilarityScore
            };

            hydrated.Add(new SearchResult
            {
                Id = doc.Id,
                Title = doc.Title,
                Content = doc.Content,
                Collection = doc.Collection,
                CreatedAt = doc.CreatedAt,
                Metadata = metadata,
                Source = result.Source,
                SimilarityScore = result.SimilarityScore
            });
        }

        return hydrated;
    }

    private sealed class EngramAggregate
    {
        public Guid DocumentId { get; init; }
        public string Collection { get; set; } = string.Empty;
        public int TokenCount { get; set; }
        public int SharedHashes { get; set; }
        public HashSet<int> MatchedLayers { get; } = new();
        public Dictionary<int, int> LayerHits { get; } = new();
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
