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
                Payload =
                {
                    ["title"] = new Value { StringValue = document.Title },
                    ["content"] = new Value { StringValue = document.Content },
                    ["collection"] = new Value { StringValue = document.Collection },
                    ["created_at"] = new Value { StringValue = document.CreatedAt.ToString("O") },
                    ["updated_at"] = new Value { StringValue = document.UpdatedAt.ToString("O") }
                }
            };

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
                var doc = new VectorDocument
                {
                    Id = Guid.Parse(point.Id.ToString()),
                    Title = point.Payload["title"].StringValue,
                    Content = point.Payload["content"].StringValue,
                    Collection = point.Payload["collection"].StringValue,
                    CreatedAt = DateTime.Parse(point.Payload["created_at"].StringValue),
                    UpdatedAt = DateTime.Parse(point.Payload["updated_at"].StringValue)
                };

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
