using System;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using VectorMcpServer.Configuration;

namespace VectorMcpServer.Services;

public interface IEmbeddingService : IDisposable
{
    Task<float[]> GenerateTextEmbeddingAsync(string text, CancellationToken cancellationToken = default);
    Task<float[]> GenerateImageEmbeddingAsync(Stream imageStream, CancellationToken cancellationToken = default);
}

public sealed class HttpEmbeddingService : IEmbeddingService
{
    private readonly HttpClient _httpClient;
    private readonly VectorStoreSettings _settings;
    private readonly ILogger<HttpEmbeddingService> _logger;
    private readonly float[] _fallbackBuffer;
    private readonly object _fallbackLock = new();
    private bool _dimensionLogged;

    public HttpEmbeddingService(HttpClient httpClient, VectorStoreSettings settings, ILogger<HttpEmbeddingService> logger)
    {
        _httpClient = httpClient;
        _settings = settings;
        _logger = logger;
        _fallbackBuffer = new float[_settings.EmbeddingDimension];

        if (_settings.EmbeddingTimeoutSeconds > 0)
        {
            _httpClient.Timeout = TimeSpan.FromSeconds(_settings.EmbeddingTimeoutSeconds);
        }
    }

    public async Task<float[]> GenerateTextEmbeddingAsync(string text, CancellationToken cancellationToken = default)
    {
        cancellationToken.ThrowIfCancellationRequested();

        if (string.IsNullOrWhiteSpace(text))
        {
            return new float[_settings.EmbeddingDimension];
        }

        if (!string.IsNullOrWhiteSpace(_settings.EmbeddingEndpoint))
        {
            var vector = await TryFetchEmbeddingAsync(text, cancellationToken);
            if (vector is not null)
            {
                return EnsureDimension(vector, "http");
            }
        }

        return HashEmbedding(text, cancellationToken);
    }

    public async Task<float[]> GenerateImageEmbeddingAsync(Stream imageStream, CancellationToken cancellationToken = default)
    {
        if (imageStream == null)
        {
            throw new ArgumentNullException(nameof(imageStream));
        }

        using var buffer = new MemoryStream();
        if (imageStream.CanSeek)
        {
            imageStream.Position = 0;
        }

        await imageStream.CopyToAsync(buffer, cancellationToken);
        var base64 = Convert.ToBase64String(buffer.ToArray());
        return HashEmbedding(base64, cancellationToken);
    }

    private async Task<float[]?> TryFetchEmbeddingAsync(string text, CancellationToken cancellationToken)
    {
        try
        {
            var payload = new { inputs = new[] { text } };
            using var request = new HttpRequestMessage(HttpMethod.Post, _settings.EmbeddingEndpoint)
            {
                Content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json")
            };

            if (!string.IsNullOrWhiteSpace(_settings.EmbeddingApiKey))
            {
                request.Headers.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _settings.EmbeddingApiKey);
            }

            using var response = await _httpClient.SendAsync(request, cancellationToken);
            var body = await response.Content.ReadAsStringAsync(cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogWarning("Embedding endpoint returned {Status}: {Body}", response.StatusCode, body);
                return null;
            }

            var vector = ParseEmbedding(body);
            if (vector == null)
            {
                _logger.LogWarning("Embedding endpoint response did not contain an embedding.");
                return null;
            }

            return vector;
        }
        catch (OperationCanceledException)
        {
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Embedding endpoint request failed.");
            return null;
        }
    }

    private static float[]? ParseEmbedding(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        if (root.ValueKind == JsonValueKind.Array)
        {
            return ReadVector(root[0]);
        }

        if (root.TryGetProperty("embeddings", out var embeddings) && embeddings.ValueKind == JsonValueKind.Array)
        {
            return ReadVector(embeddings[0]);
        }

        if (root.TryGetProperty("data", out var data) && data.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in data.EnumerateArray())
            {
                if (item.TryGetProperty("embedding", out var embedding))
                {
                    return ReadVector(embedding);
                }
            }
        }

        if (root.TryGetProperty("embedding", out var singleEmbedding))
        {
            return ReadVector(singleEmbedding);
        }

        if (root.TryGetProperty("vector", out var vector))
        {
            return ReadVector(vector);
        }

        return null;
    }

    private static float[]? ReadVector(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Array)
        {
            return null;
        }

        var length = element.GetArrayLength();
        var vector = new float[length];
        var index = 0;

        foreach (var value in element.EnumerateArray())
        {
            vector[index++] = value.ValueKind == JsonValueKind.Number ? (float)value.GetDouble() : 0f;
        }

        return vector;
    }

    private float[] HashEmbedding(string text, CancellationToken cancellationToken)
    {
        var source = text ?? string.Empty;
        var bytes = Encoding.UTF8.GetBytes(source);

        lock (_fallbackLock)
        {
            Array.Clear(_fallbackBuffer, 0, _fallbackBuffer.Length);
            Span<byte> hash = stackalloc byte[32];
            var offset = 0;

            while (offset < bytes.Length)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var length = Math.Min(1024, bytes.Length - offset);
                SHA256.HashData(bytes.AsSpan(offset, length), hash);
                offset += length;
                AccumulateHash(hash);
            }

            Normalize(_fallbackBuffer);
            return _fallbackBuffer.ToArray();
        }
    }

    private float[] EnsureDimension(float[] vector, string source)
    {
        if (vector.Length == _settings.EmbeddingDimension)
        {
            return vector;
        }

        var adjusted = new float[_settings.EmbeddingDimension];
        Array.Copy(vector, adjusted, Math.Min(vector.Length, adjusted.Length));

        if (!_dimensionLogged)
        {
            _logger.LogWarning(
                "Embedding dimension {Actual} does not match target {Target}. Padding/truncating ({Source}).",
                vector.Length,
                _settings.EmbeddingDimension,
                source);
            _dimensionLogged = true;
        }

        return adjusted;
    }

    private void AccumulateHash(ReadOnlySpan<byte> hash)
    {
        for (int i = 0; i < hash.Length && i < _fallbackBuffer.Length; i++)
        {
            _fallbackBuffer[i] += (hash[i] - 128) / 128f;
        }
    }

    private static void Normalize(float[] vector)
    {
        var norm = MathF.Sqrt(vector.Sum(v => v * v));
        if (norm <= 0)
        {
            return;
        }

        var inv = 1f / norm;
        for (int i = 0; i < vector.Length; i++)
        {
            vector[i] *= inv;
        }
    }

    public void Dispose()
    {
    }
}
