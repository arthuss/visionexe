using Microsoft.AspNetCore.SignalR;
using VectorMcpServer.Data;
using VectorMcpServer.Services;
using Microsoft.EntityFrameworkCore;

namespace ExegetOS.Management.Web.Hubs;

public class VectorMcpHub : Hub
{
    private readonly VectorDbContext _dbContext;
    private readonly IQdrantService _qdrantService;
    private readonly ILogger<VectorMcpHub> _logger;

    public VectorMcpHub(
        VectorDbContext dbContext,
        IQdrantService qdrantService,
        ILogger<VectorMcpHub> logger)
    {
        _dbContext = dbContext;
        _qdrantService = qdrantService;
        _logger = logger;
    }

    public async Task JoinVectorGroup()
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, "VectorUpdates");
        _logger.LogInformation("Client {ConnectionId} joined vector updates", Context.ConnectionId);
    }

    public async Task LeaveVectorGroup()
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, "VectorUpdates");
        _logger.LogInformation("Client {ConnectionId} left vector updates", Context.ConnectionId);
    }

    public async Task GetVectorSystemStatus()
    {
        try
        {
            // PostgreSQL Vector Status
            var totalDocuments = await _dbContext.Documents.CountAsync();
            var collections = await _dbContext.Documents
                .GroupBy(d => d.Collection)
                .Select(g => new { Collection = g.Key, Count = g.Count() })
                .ToListAsync();

            // Qdrant Status
            var qdrantCollections = await _qdrantService.GetCollectionsAsync();

            var vectorStatus = new
            {
                PostgreSQL = new
                {
                    IsConnected = await _dbContext.Database.CanConnectAsync(),
                    TotalDocuments = totalDocuments,
                    Collections = collections
                },
                Qdrant = new
                {
                    IsConnected = qdrantCollections.Count > 0,
                    Collections = qdrantCollections
                },
                Timestamp = DateTime.UtcNow
            };

            await Clients.Caller.SendAsync("VectorSystemStatusUpdate", vectorStatus);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting vector system status");
            await Clients.Caller.SendAsync("VectorSystemStatusError", ex.Message);
        }
    }

    public async Task GetCollectionMetrics(string collectionName)
    {
        try
        {
            var documents = await _dbContext.Documents
                .Where(d => d.Collection == collectionName)
                .Select(d => new
                {
                    d.Id,
                    d.Title,
                    d.CreatedAt,
                    d.UpdatedAt,
                    HasEmbedding = d.Embedding != null,
                    MetadataCount = d.Metadata.Count
                })
                .ToListAsync();

            await Clients.Caller.SendAsync("CollectionMetricsUpdate", new
            {
                Collection = collectionName,
                Documents = documents,
                TotalCount = documents.Count,
                WithEmbeddings = documents.Count(d => d.HasEmbedding),
                Timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting collection metrics for {Collection}", collectionName);
            await Clients.Caller.SendAsync("CollectionMetricsError", ex.Message);
        }
    }

    public async Task BroadcastVectorOperation(string operation, string collection, string documentId)
    {
        await Clients.Group("VectorUpdates").SendAsync("VectorOperationUpdate", new
        {
            Operation = operation, // "store", "search", "delete"
            Collection = collection,
            DocumentId = documentId,
            Timestamp = DateTime.UtcNow,
            ConnectionId = Context.ConnectionId
        });
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, "VectorUpdates");
        await base.OnDisconnectedAsync(exception);
    }
}
