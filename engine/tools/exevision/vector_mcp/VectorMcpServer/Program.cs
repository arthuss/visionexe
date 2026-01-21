using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using ModelContextProtocol;
using VectorMcpServer.Configuration;
using VectorMcpServer.Data;
using VectorMcpServer.Services;

var builder = Host.CreateApplicationBuilder(args);

DotEnv.Load(
    Path.Combine(Directory.GetCurrentDirectory(), ".env"),
    Path.Combine(AppContext.BaseDirectory, ".env"));

var vectorSettings = VectorStoreSettings.FromConfiguration(builder.Configuration);

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

var app = builder.Build();

// Ensure database is created and migrations are applied
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<VectorDbContext>();
    await dbContext.Database.EnsureCreatedAsync();
}

await app.RunAsync();
