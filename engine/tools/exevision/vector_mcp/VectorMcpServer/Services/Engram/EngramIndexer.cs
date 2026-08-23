using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using Microsoft.ML.Tokenizers;
using VectorMcpServer.Configuration;

namespace VectorMcpServer.Services.Engram;

public interface IEngramIndexer
{
    bool IsEnabled { get; }
    EngramHashResult? ComputeHashes(string text);
}

public sealed class EngramHashResult
{
    public EngramHashResult(int tokenCount, IReadOnlyDictionary<int, long[]> layerHashes)
    {
        TokenCount = tokenCount;
        LayerHashes = layerHashes;
    }

    public int TokenCount { get; }
    public IReadOnlyDictionary<int, long[]> LayerHashes { get; }
}

public sealed class EngramIndexer : IEngramIndexer
{
    private readonly ILogger<EngramIndexer> _logger;
    private readonly EngramParams? _params;
    private readonly CodeGenTokenizer? _tokenizer;
    private readonly int _maxNgramSize;
    private readonly int _numHeads;
    private readonly int[] _layerIds;
    private readonly int _lookupLimit;

    public EngramIndexer(VectorStoreSettings settings, EngramLoader loader, ILogger<EngramIndexer> logger)
    {
        _logger = logger;
        _params = loader.Load(settings.EngramParamsPath);
        _tokenizer = _params != null ? CreateTokenizer(settings.EngramTokenizerDir) : null;

        if (_params == null || _tokenizer == null)
        {
            IsEnabled = false;
            _maxNgramSize = 0;
            _numHeads = 0;
            _layerIds = Array.Empty<int>();
            _lookupLimit = 0;
            return;
        }

        IsEnabled = true;
        _maxNgramSize = _params.Metadata.MaxNgramSize;
        _numHeads = _params.Metadata.NumHeads;
        _layerIds = _params.Metadata.LayerIds;
        _lookupLimit = Math.Max(_tokenizer.Vocabulary.Count, _params.Metadata.VocabSize);
    }

    public bool IsEnabled { get; }

    public EngramHashResult? ComputeHashes(string text)
    {
        if (!IsEnabled || _params == null || _tokenizer == null)
        {
            return null;
        }

        if (string.IsNullOrWhiteSpace(text))
        {
            return new EngramHashResult(0, new Dictionary<int, long[]>());
        }

        IReadOnlyList<int> rawIds;
        try
        {
            rawIds = _tokenizer.EncodeToIds(
                text,
                addPrefixSpace: false,
                addBeginningOfSentence: false,
                addEndOfSentence: false,
                considerPreTokenization: true,
                considerNormalization: true);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Engram tokenization failed.");
            return null;
        }

        var tokenIds = new long[rawIds.Count];
        var clampMax = _lookupLimit > 0 ? _lookupLimit - 1 : int.MaxValue;
        for (var i = 0; i < rawIds.Count; i++)
        {
            var value = rawIds[i];
            if (value < 0)
            {
                value = 0;
            }
            else if (value > clampMax)
            {
                value = clampMax;
            }

            tokenIds[i] = value;
        }

        var results = new Dictionary<int, long[]>();

        for (var layerIdx = 0; layerIdx < _layerIds.Length; layerIdx++)
        {
            var layerId = _layerIds[layerIdx];
            var mults = _params.Hashing.Multipliers[layerIdx];
            var modulos = _params.Hashing.Modulos[layerIdx];
            var offsets = _params.Hashing.Offsets[layerIdx];

            var layerHashes = new HashSet<long>();

            for (var pos = 0; pos < tokenIds.Length; pos++)
            {
                var shifts = new long[_maxNgramSize];
                shifts[0] = tokenIds[pos];
                for (var k = 1; k < _maxNgramSize; k++)
                {
                    var idx = pos - k;
                    shifts[k] = idx >= 0 ? tokenIds[idx] : 0;
                }

                for (var n = 2; n <= _maxNgramSize; n++)
                {
                    var mix = unchecked(shifts[0] * mults[0]);
                    for (var k = 1; k < n; k++)
                    {
                        mix = unchecked(mix ^ (shifts[k] * mults[k]));
                    }

                    var headMods = modulos[n - 2];
                    var headOffsets = offsets[n - 2];
                    for (var head = 0; head < _numHeads; head++)
                    {
                        var hash = PositiveMod(mix, headMods[head]) + headOffsets[head];
                        layerHashes.Add(hash);
                    }
                }
            }

            results[layerId] = layerHashes.OrderBy(h => h).ToArray();
        }

        return new EngramHashResult(tokenIds.Length, results);
    }

    private CodeGenTokenizer? CreateTokenizer(string? tokenizerDir)
    {
        var resolved = EngramLoader.ResolveTokenizerDir(tokenizerDir);
        if (string.IsNullOrWhiteSpace(resolved))
        {
            _logger.LogWarning("Engram tokenizer directory not found. Set ENGRAM_TOKENIZER_DIR.");
            return null;
        }

        var vocabPath = Path.Combine(resolved, "vocab.json");
        var mergesPath = Path.Combine(resolved, "merges.txt");

        if (!File.Exists(vocabPath) || !File.Exists(mergesPath))
        {
            _logger.LogWarning("Engram tokenizer files missing in {Dir}", resolved);
            return null;
        }

        using var vocabStream = OpenCompatibleVocabStream(vocabPath);
        using var mergesStream = File.OpenRead(mergesPath);

        try
        {
            var tokenizer = CodeGenTokenizer.Create(
                vocabStream,
                mergesStream,
                addPrefixSpace: false,
                addBeginOfSentence: false,
                addEndOfSentence: false);

            _logger.LogInformation("Engram tokenizer loaded from {Dir}", resolved);
            return tokenizer;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Engram tokenizer initialization failed for {Dir}", resolved);
            return null;
        }
    }

    private Stream OpenCompatibleVocabStream(string vocabPath)
    {
        try
        {
            var rawJson = File.ReadAllText(vocabPath);
            var vocab = JsonSerializer.Deserialize<Dictionary<string, int>>(rawJson);
            if (vocab != null &&
                !vocab.ContainsKey("<|endoftext|>"))
            {
                var nextId = vocab.Count > 0 ? vocab.Values.Max() + 1 : 0;
                vocab["<|endoftext|>"] = nextId;
                _logger.LogInformation(
                    "Patched tokenizer vocab: injected <|endoftext|> with id={UnknownId}.",
                    nextId);
                var patchedJson = JsonSerializer.Serialize(vocab);
                return new MemoryStream(Encoding.UTF8.GetBytes(patchedJson), writable: false);
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to inspect tokenizer vocab for compatibility. Using raw vocab file.");
        }

        return File.OpenRead(vocabPath);
    }

    private static long PositiveMod(long value, long modulus)
    {
        if (modulus == 0)
        {
            return 0;
        }

        var rem = value % modulus;
        return rem < 0 ? rem + modulus : rem;
    }
}
