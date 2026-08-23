using System;
using System.Text.Json.Serialization;

namespace VectorMcpServer.Services.Engram;

public sealed class EngramParams
{
    [JsonPropertyName("metadata")]
    public EngramMetadata Metadata { get; init; } = new();

    [JsonPropertyName("hashing")]
    public EngramHashing Hashing { get; init; } = new();
}

public sealed class EngramMetadata
{
    [JsonPropertyName("version")]
    public string? Version { get; init; }

    [JsonPropertyName("vocab_size")]
    public int VocabSize { get; init; }

    [JsonPropertyName("max_ngram_size")]
    public int MaxNgramSize { get; init; }

    [JsonPropertyName("num_heads")]
    public int NumHeads { get; init; }

    [JsonPropertyName("layer_ids")]
    public int[] LayerIds { get; init; } = Array.Empty<int>();

    [JsonPropertyName("seed")]
    public int Seed { get; init; }
}

public sealed class EngramHashing
{
    [JsonPropertyName("multipliers")]
    public long[][] Multipliers { get; init; } = Array.Empty<long[]>();

    [JsonPropertyName("modulos")]
    public long[][][] Modulos { get; init; } = Array.Empty<long[][]>();

    [JsonPropertyName("offsets")]
    public long[][][] Offsets { get; init; } = Array.Empty<long[][]>();
}
