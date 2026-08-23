using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace VectorMcpServer.Services.Engram;

public sealed class EngramLoader
{
    private readonly ILogger<EngramLoader> _logger;

    public EngramLoader(ILogger<EngramLoader> logger)
    {
        _logger = logger;
    }

    public EngramParams? Load(string? paramsPath)
    {
        var resolved = ResolveParamsPath(paramsPath);
        if (string.IsNullOrWhiteSpace(resolved) || !File.Exists(resolved))
        {
            _logger.LogWarning("Engram params not found. Skipping Engram indexer initialization.");
            return null;
        }

        try
        {
            var json = File.ReadAllText(resolved);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

            var data = JsonSerializer.Deserialize<EngramParams>(json, options);
            if (data == null)
            {
                _logger.LogWarning("Engram params could not be deserialized: {Path}", resolved);
                return null;
            }

            if (!Validate(data, out var error))
            {
                _logger.LogWarning("Engram params validation failed: {Error}", error);
                return null;
            }

            _logger.LogInformation("Engram params loaded from {Path}", resolved);
            return data;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to load Engram params.");
            return null;
        }
    }

    public static string? ResolveParamsPath(string? paramsPath)
    {
        foreach (var candidate in ResolveCandidates(paramsPath, "engram_params.json", "Engram", "engram_params.json"))
        {
            if (File.Exists(candidate))
            {
                return candidate;
            }
        }

        return null;
    }

    public static string? ResolveTokenizerDir(string? tokenizerDir)
    {
        foreach (var candidate in ResolveCandidates(tokenizerDir, "tokenizer.json", "Models", "Qwen3-VL-2B-Instruct"))
        {
            if (Directory.Exists(candidate))
            {
                return candidate;
            }

            if (File.Exists(candidate) &&
                string.Equals(Path.GetFileName(candidate), "tokenizer.json", StringComparison.OrdinalIgnoreCase))
            {
                return Path.GetDirectoryName(candidate);
            }
        }

        return null;
    }

    private static bool Validate(EngramParams data, out string error)
    {
        error = string.Empty;

        if (data.Metadata.LayerIds.Length == 0)
        {
            error = "metadata.layer_ids is empty";
            return false;
        }

        if (data.Metadata.MaxNgramSize < 2)
        {
            error = "metadata.max_ngram_size must be >= 2";
            return false;
        }

        if (data.Metadata.NumHeads <= 0)
        {
            error = "metadata.num_heads must be > 0";
            return false;
        }

        if (data.Hashing.Multipliers.Length == 0 ||
            data.Hashing.Modulos.Length == 0 ||
            data.Hashing.Offsets.Length == 0)
        {
            error = "hashing arrays are empty";
            return false;
        }

        if (data.Hashing.Multipliers.Length != data.Metadata.LayerIds.Length)
        {
            error = "hashing.multipliers layer count mismatch";
            return false;
        }

        if (data.Hashing.Modulos.Length != data.Metadata.LayerIds.Length ||
            data.Hashing.Offsets.Length != data.Metadata.LayerIds.Length)
        {
            error = "hashing.modulos/offsets layer count mismatch";
            return false;
        }

        return true;
    }

    private static string[] ResolveCandidates(string? explicitPath, string leafName, params string[] defaultSegments)
    {
        var candidates = new System.Collections.Generic.List<string>();

        if (!string.IsNullOrWhiteSpace(explicitPath))
        {
            if (Path.IsPathRooted(explicitPath))
            {
                candidates.Add(explicitPath);
            }
            else
            {
                candidates.Add(Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), explicitPath)));
                candidates.Add(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, explicitPath)));
            }
        }

        var exevisionRoot = ResolveExevisionRoot();
        if (!string.IsNullOrWhiteSpace(exevisionRoot))
        {
            var defaultPath = Path.Combine(exevisionRoot, Path.Combine(defaultSegments));
            candidates.Add(defaultPath);
        }

        if (!string.IsNullOrWhiteSpace(leafName))
        {
            var cwdLeaf = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), leafName));
            candidates.Add(cwdLeaf);
        }

        return candidates.Distinct(StringComparer.OrdinalIgnoreCase).ToArray();
    }

    private static string? ResolveExevisionRoot()
    {
        try
        {
            var baseDir = AppContext.BaseDirectory;
            var projectDir = Path.GetFullPath(Path.Combine(baseDir, "..", "..", ".."));
            var vectorMcpDir = Path.GetFullPath(Path.Combine(projectDir, ".."));
            var exevisionDir = Path.GetFullPath(Path.Combine(vectorMcpDir, ".."));
            return exevisionDir;
        }
        catch
        {
            return null;
        }
    }
}
