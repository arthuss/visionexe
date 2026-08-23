using Microsoft.Extensions.Logging;
using Qdrant.Client;
using Qdrant.Client.Grpc;
using VectorMcpServer.Configuration;
using VectorMcpServer.Models;

namespace VectorMcpServer.Services;

public interface IQdrantService
{
    Task<bool> CreateCollectionAsync(string collectionName, uint? vectorSize = null);
    Task<bool> UpsertPointAsync(string collectionName, VectorDocument document);
    Task<List<VectorDocument>> SearchAsync(string collectionName, float[] queryVector, uint limit = 10, float threshold = 0.7f);
    Task<bool> DeletePointAsync(string collectionName, Guid documentId);
    Task<List<string>> GetCollectionsAsync();
}

public class QdrantService : IQdrantService
{
    private readonly QdrantClient _client;
    private readonly VectorStoreSettings _settings;
    private readonly ILogger<QdrantService> _logger;
    private static readonly HashSet<string> ReservedPayloadKeys = new(StringComparer.OrdinalIgnoreCase)
    {
        "title",
        "content",
        "collection",
        "created_at",
        "updated_at"
    };

    public QdrantService(VectorStoreSettings settings, ILogger<QdrantService> logger)
    {
        _settings = settings;
        _logger = logger;
        _client = new QdrantClient(settings.QdrantHost, settings.QdrantGrpcPort, https: false);
    }

    public async Task<bool> CreateCollectionAsync(string collectionName, uint? vectorSize = null)
    {
        try
        {
            var collections = await _client.ListCollectionsAsync();
            if (collections.Contains(collectionName))
            {
                return true;
            }

            var size = vectorSize ?? (uint)_settings.EmbeddingDimension;
            await _client.CreateCollectionAsync(collectionName, new VectorParams
            {
                Size = size,
                Distance = Distance.Cosine
            });

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to create Qdrant collection {Collection}", collectionName);
            return false;
        }
    }

    public async Task<bool> UpsertPointAsync(string collectionName, VectorDocument document)
    {
        try
        {
            if (document.Embedding == null)
            {
                return false;
            }

            var point = new PointStruct
            {
                Id = new PointId { Uuid = document.Id.ToString() },
                Vectors = document.Embedding.ToArray(),
                Payload = { }
            };

            var minimalPayload = IsMinimalPayload();
            point.Payload["title"] = new Value { StringValue = document.Title };
            point.Payload["collection"] = new Value { StringValue = document.Collection };
            point.Payload["created_at"] = new Value { StringValue = document.CreatedAt.ToString("O") };
            point.Payload["updated_at"] = new Value { StringValue = document.UpdatedAt.ToString("O") };
            if (!minimalPayload)
            {
                point.Payload["content"] = new Value { StringValue = document.Content };
            }

            foreach (var kvp in document.Metadata)
            {
                point.Payload[kvp.Key] = new Value { StringValue = kvp.Value?.ToString() ?? string.Empty };
            }

            await _client.UpsertAsync(collectionName, new[] { point });
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to upsert Qdrant point {DocumentId}", document.Id);
            return false;
        }
    }

    public async Task<List<VectorDocument>> SearchAsync(string collectionName, float[] queryVector, uint limit = 10, float threshold = 0.7f)
    {
        try
        {
            var searchResult = await _client.SearchAsync(collectionName, queryVector, limit: limit, scoreThreshold: threshold);

            var documents = new List<VectorDocument>();

            foreach (var point in searchResult)
            {
                var payload = point.Payload;
                var doc = new VectorDocument
                {
                    Id = Guid.Parse(point.Id.ToString()),
                    Title = ReadPayloadString(payload, "title"),
                    Content = ReadPayloadString(payload, "content"),
                    Collection = ReadPayloadString(payload, "collection") ?? collectionName,
                    CreatedAt = ReadPayloadDate(payload, "created_at"),
                    UpdatedAt = ReadPayloadDate(payload, "updated_at")
                };

                foreach (var kvp in payload)
                {
                    if (ReservedPayloadKeys.Contains(kvp.Key))
                    {
                        continue;
                    }
                    doc.Metadata[kvp.Key] = ReadPayloadValue(kvp.Value);
                }

                doc.Metadata["score"] = point.Score;

                documents.Add(doc);
            }

            return documents;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to search Qdrant collection {Collection}", collectionName);
            return new List<VectorDocument>();
        }
    }

    private bool IsMinimalPayload()
    {
        return string.Equals(_settings.QdrantPayloadMode, "minimal", StringComparison.OrdinalIgnoreCase);
    }

    private static string? ReadPayloadString(IDictionary<string, Value> payload, string key)
    {
        if (!payload.TryGetValue(key, out var value))
        {
            return null;
        }
        return value.StringValue;
    }

    private static DateTime ReadPayloadDate(IDictionary<string, Value> payload, string key)
    {
        var raw = ReadPayloadString(payload, key);
        if (raw != null && DateTime.TryParse(raw, out var parsed))
        {
            return parsed;
        }
        return DateTime.UtcNow;
    }

    private static object ReadPayloadValue(Value value)
    {
        if (!string.IsNullOrWhiteSpace(value.StringValue))
        {
            return value.StringValue;
        }
        if (value.IntegerValue != 0)
        {
            return value.IntegerValue;
        }
        if (Math.Abs(value.DoubleValue) > 0)
        {
            return value.DoubleValue;
        }
        if (value.BoolValue)
        {
            return value.BoolValue;
        }
        if (value.ListValue is { Values.Count: > 0 })
        {
            return value.ListValue.Values.Select(ReadPayloadValue).ToList();
        }
        if (value.StructValue is { Fields.Count: > 0 })
        {
            return value.StructValue.Fields.ToDictionary(pair => pair.Key, pair => ReadPayloadValue(pair.Value));
        }
        return string.Empty;
    }

    public async Task<bool> DeletePointAsync(string collectionName, Guid documentId)
    {
        try
        {
            var pointId = new PointId { Uuid = documentId.ToString() };
            await _client.DeleteAsync(collectionName, new[] { pointId });
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to delete Qdrant point {DocumentId}", documentId);
            return false;
        }
    }

    public async Task<List<string>> GetCollectionsAsync()
    {
        try
        {
            var collections = await _client.ListCollectionsAsync();
            return collections.ToList();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to list Qdrant collections");
            return new List<string>();
        }
    }
}
