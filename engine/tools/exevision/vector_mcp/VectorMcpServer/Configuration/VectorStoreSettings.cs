using System;
using Microsoft.Extensions.Configuration;

namespace VectorMcpServer.Configuration;

public sealed class VectorStoreSettings
{
    public string PostgresHost { get; init; } = "localhost";
    public int PostgresPort { get; init; } = 5432;
    public string PostgresDatabase { get; init; } = "exegetos";
    public string PostgresUser { get; init; } = "exegetos_user";
    public string PostgresPassword { get; init; } = "dev_password";
    public string? PostgresConnectionStringOverride { get; init; }

    public string QdrantHost { get; init; } = "localhost";
    public int QdrantGrpcPort { get; init; } = 6334;
    public int QdrantHttpPort { get; init; } = 6333;
    public string QdrantPayloadMode { get; init; } = "minimal";

    public int EmbeddingDimension { get; init; } = 1024;
    public string? EmbeddingEndpoint { get; init; }
    public string? EmbeddingApiKey { get; init; }
    public int EmbeddingTimeoutSeconds { get; init; } = 30;
    public string? EmbeddingQueryPrefix { get; init; }

    public string? DeleteToken { get; init; }
    public string? EngramParamsPath { get; init; }
    public string? EngramTokenizerDir { get; init; }

    public string BuildPostgresConnectionString()
    {
        if (!string.IsNullOrWhiteSpace(PostgresConnectionStringOverride))
        {
            return PostgresConnectionStringOverride;
        }

        return $"Host={PostgresHost};Port={PostgresPort};Database={PostgresDatabase};Username={PostgresUser};Password={PostgresPassword}";
    }

    public static VectorStoreSettings FromConfiguration(IConfiguration configuration)
    {
        var connectionOverride = GetSetting(configuration, "VECTOR_DB_CONNECTION", "DB_CONNECTION");

        return new VectorStoreSettings
        {
            PostgresHost = GetSetting(configuration, "VECTOR_DB_HOST", "DB_HOST") ?? "localhost",
            PostgresPort = GetIntSetting(configuration, 5432, "VECTOR_DB_PORT", "DB_PORT"),
            PostgresDatabase = GetSetting(configuration, "VECTOR_DB_NAME", "DB_NAME") ?? "exegetos",
            PostgresUser = GetSetting(configuration, "VECTOR_DB_USER", "AGENT_USER", "ADMIN_USER") ?? "exegetos_user",
            PostgresPassword = GetSetting(configuration, "VECTOR_DB_PASSWORD", "AGENT_PASSWORD", "ADMIN_PASSWORD") ?? "dev_password",
            PostgresConnectionStringOverride = connectionOverride,
            QdrantHost = GetSetting(configuration, "QDRANT_HOST") ?? "localhost",
            QdrantGrpcPort = GetIntSetting(configuration, 6334, "QDRANT_GRPC_PORT", "QDRANT_PORT"),
            QdrantHttpPort = GetIntSetting(configuration, 6333, "QDRANT_HTTP_PORT"),
            QdrantPayloadMode = GetSetting(configuration, "QDRANT_PAYLOAD_MODE") ?? "minimal",
            EmbeddingDimension = GetIntSetting(configuration, 1024, "EMBEDDING_DIMENSION", "VECTOR_EMBEDDING_DIMENSION"),
            EmbeddingEndpoint = GetSetting(configuration, "EMBEDDING_ENDPOINT", "VECTOR_EMBEDDING_ENDPOINT"),
            EmbeddingApiKey = GetSetting(configuration, "EMBEDDING_API_KEY"),
            EmbeddingTimeoutSeconds = GetIntSetting(configuration, 30, "EMBEDDING_TIMEOUT_SECONDS"),
            EmbeddingQueryPrefix = GetSetting(configuration, "EMBEDDING_QUERY_PREFIX"),
            DeleteToken = GetSetting(configuration, "VECTOR_DELETE_TOKEN"),
            EngramParamsPath = GetSetting(configuration, "ENGRAM_PARAMS_PATH"),
            EngramTokenizerDir = GetSetting(configuration, "ENGRAM_TOKENIZER_DIR")
        };
    }

    private static string? GetSetting(IConfiguration configuration, params string[] keys)
    {
        foreach (var key in keys)
        {
            if (string.IsNullOrWhiteSpace(key))
            {
                continue;
            }

            var env = Environment.GetEnvironmentVariable(key);
            if (!string.IsNullOrWhiteSpace(env))
            {
                return env;
            }

            var configValue = configuration[key];
            if (!string.IsNullOrWhiteSpace(configValue))
            {
                return configValue;
            }
        }

        return null;
    }

    private static int GetIntSetting(IConfiguration configuration, int defaultValue, params string[] keys)
    {
        var value = GetSetting(configuration, keys);
        if (int.TryParse(value, out var parsed) && parsed > 0)
        {
            return parsed;
        }

        return defaultValue;
    }
}
