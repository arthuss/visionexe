using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol;
using Npgsql;
using VectorMcpServer.Configuration;
using VectorMcpServer.Data;
using VectorMcpServer.Services;
using VectorMcpServer.Services.Engram;

var builder = Host.CreateApplicationBuilder(args);

builder.Logging.ClearProviders();
builder.Logging.AddConsole(options =>
{
    options.TimestampFormat = "HH:mm:ss ";
    options.LogToStandardErrorThreshold = LogLevel.Information;
});

var baseDir = AppContext.BaseDirectory;
var projectDir = Path.GetFullPath(Path.Combine(baseDir, "..", "..", ".."));
var vectorMcpDir = Path.GetFullPath(Path.Combine(projectDir, ".."));

DotEnv.Load(
    Path.Combine(Directory.GetCurrentDirectory(), ".env"),
    Path.Combine(baseDir, ".env"),
    Path.Combine(projectDir, ".env"),
    Path.Combine(vectorMcpDir, ".env"));

var vectorSettings = VectorStoreSettings.FromConfiguration(builder.Configuration);

NpgsqlConnection.GlobalTypeMapper.EnableDynamicJson();

// Add MCP Server with STDIO transport
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithToolsFromAssembly();

// Add Entity Framework with PostgreSQL
builder.Services.AddDbContext<VectorDbContext>(options =>
    options.UseNpgsql(
        vectorSettings.BuildPostgresConnectionString(),
        npgsqlOptions => npgsqlOptions.UseVector()));

// Add custom services
builder.Services.AddSingleton(vectorSettings);
builder.Services.AddHttpClient<IEmbeddingService, HttpEmbeddingService>();
builder.Services.AddSingleton<IQdrantService, QdrantService>();
builder.Services.AddSingleton<EngramLoader>();
builder.Services.AddSingleton<IEngramIndexer, EngramIndexer>();

var app = builder.Build();

// Ensure database is created and migrations are applied
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<VectorDbContext>();
    await dbContext.Database.EnsureCreatedAsync();
    await SchemaBootstrapper.EnsureSchemaAsync(dbContext);
}

await app.RunAsync();
