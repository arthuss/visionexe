using System;
using System.ComponentModel;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using ModelContextProtocol.Server;
using VectorMcpServer.Configuration;
using VectorMcpServer.Data;
using VectorMcpServer.Models;

namespace VectorMcpServer.Tools;

[McpServerToolType]
public class CanonicalTools
{
    [McpServerTool]
    [Description("Create a run record for an analysis or generation pass")]
    public static async Task<string> CreateRun(
        VectorDbContext dbContext,
        [Description("Run type (analysis, generation, ingestion, etc.)")] string runType,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Unit ref (optional)")] string? unitRef = null,
        [Description("Input sha256 (optional)")] string? inputSha256 = null,
        [Description("Prompt bundle sha (optional)")] string? promptBundleSha = null,
        [Description("Model id (optional)")] string? modelId = null,
        [Description("Settings JSON (optional)")] string? settings = null,
        [Description("Inputs JSON (optional)")] string? inputs = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            var run = new RunRecord
            {
                RunType = runType,
                StoryId = storyId,
                TimelineId = timelineId,
                UnitRef = unitRef,
                InputSha256 = inputSha256,
                PromptBundleSha = promptBundleSha,
                ModelId = modelId,
                Settings = ParseJsonMap(settings),
                Inputs = ParseJsonMap(inputs),
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.Runs.Add(run);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                run_id = run.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Store an artifact record in the canonical store")]
    public static async Task<string> StoreArtifact(
        VectorDbContext dbContext,
        [Description("Artifact kind (analysis, image, mask, latent, audio, json, text, etc.)")] string kind,
        [Description("Sha256 of content or file (optional)")] string? sha256 = null,
        [Description("Inline text content (optional)")] string? content = null,
        [Description("Storage path (optional)")] string? storagePath = null,
        [Description("Mime type (optional)")] string? mime = null,
        [Description("Size in bytes (optional)")] long? sizeBytes = null,
        [Description("Run id (optional)")] string? runId = null,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Unit ref (optional)")] string? unitRef = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            Guid? runGuid = null;
            if (!string.IsNullOrWhiteSpace(runId))
            {
                if (!Guid.TryParse(runId, out var parsed))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid run_id format" });
                }
                runGuid = parsed;
            }

            var artifact = new ArtifactRecord
            {
                Kind = kind,
                Sha256 = sha256,
                Content = content,
                StoragePath = storagePath,
                Mime = mime,
                SizeBytes = sizeBytes,
                RunId = runGuid,
                StoryId = storyId,
                TimelineId = timelineId,
                UnitRef = unitRef,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.Artifacts.Add(artifact);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                artifact_id = artifact.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Link a run to an artifact output")]
    public static async Task<string> LinkRunOutput(
        VectorDbContext dbContext,
        [Description("Run id")] string runId,
        [Description("Artifact id")] string artifactId,
        [Description("Output role (primary, preview, mask, etc.)")] string role,
        [Description("Ordinal (optional)")] int? ordinal = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            if (!Guid.TryParse(runId, out var runGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid run_id format" });
            }
            if (!Guid.TryParse(artifactId, out var artifactGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid artifact_id format" });
            }

            var link = new RunOutput
            {
                RunId = runGuid,
                ArtifactId = artifactGuid,
                Role = role,
                Ordinal = ordinal,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.RunOutputs.Add(link);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                run_output_id = link.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Store a text unit (canonical input text)")]
    public static async Task<string> StoreTextUnit(
        VectorDbContext dbContext,
        [Description("Unit ref (segment/chapter id)")] string unitRef,
        [Description("Text content")] string content,
        [Description("Sha256 of content (optional)")] string? sha256 = null,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Chapter id (optional)")] string? chapterId = null,
        [Description("Segment label (optional)")] string? segmentLabel = null,
        [Description("Segment type (optional)")] string? segmentType = null,
        [Description("Verse id (optional)")] string? verseId = null,
        [Description("Scene id (optional)")] string? sceneId = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            var unit = new TextUnit
            {
                UnitRef = unitRef,
                Content = content,
                Sha256 = sha256,
                StoryId = storyId,
                TimelineId = timelineId,
                ChapterId = chapterId,
                SegmentLabel = segmentLabel,
                SegmentType = segmentType,
                VerseId = verseId,
                SceneId = sceneId,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.TextUnits.Add(unit);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                text_unit_id = unit.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Store an analysis artifact for a text unit")]
    public static async Task<string> StoreAnalysisArtifact(
        VectorDbContext dbContext,
        [Description("Analysis type (graphematic, morphologic, synthactic, semantic_historical, etc.)")] string? analysisType = null,
        [Description("Text unit id (optional)")] string? textUnitId = null,
        [Description("Unit ref (optional, resolves latest text unit)")] string? unitRef = null,
        [Description("Artifact id (optional)")] string? artifactId = null,
        [Description("Inline content (optional)")] string? content = null,
        [Description("Sha256 of analysis content (optional)")] string? sha256 = null,
        [Description("Prompt bundle sha (optional)")] string? promptBundleSha = null,
        [Description("Model id (optional)")] string? modelId = null,
        [Description("Settings JSON (optional)")] string? settings = null,
        [Description("Run id (optional)")] string? runId = null,
        [Description("Supersedes analysis id (optional)")] string? supersedesId = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            Guid? textUnitGuid = null;
            if (!string.IsNullOrWhiteSpace(textUnitId))
            {
                if (!Guid.TryParse(textUnitId, out var parsed))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid text_unit_id format" });
                }
                textUnitGuid = parsed;
            }
            else if (!string.IsNullOrWhiteSpace(unitRef))
            {
                var latest = await dbContext.TextUnits
                    .Where(t => t.UnitRef == unitRef)
                    .OrderByDescending(t => t.CreatedAt)
                    .FirstOrDefaultAsync();
                textUnitGuid = latest?.Id;
            }

            Guid? artifactGuid = null;
            if (!string.IsNullOrWhiteSpace(artifactId))
            {
                if (!Guid.TryParse(artifactId, out var parsedArtifact))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid artifact_id format" });
                }
                artifactGuid = parsedArtifact;
            }

            Guid? runGuid = null;
            if (!string.IsNullOrWhiteSpace(runId))
            {
                if (!Guid.TryParse(runId, out var parsedRun))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid run_id format" });
                }
                runGuid = parsedRun;
            }

            Guid? supersedesGuid = null;
            if (!string.IsNullOrWhiteSpace(supersedesId))
            {
                if (!Guid.TryParse(supersedesId, out var parsedSupersedes))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "Invalid supersedes_id format" });
                }
                supersedesGuid = parsedSupersedes;
            }

            var analysis = new AnalysisArtifact
            {
                TextUnitId = textUnitGuid,
                AnalysisType = analysisType,
                ArtifactId = artifactGuid,
                Content = content,
                Sha256 = sha256,
                PromptBundleSha = promptBundleSha,
                ModelId = modelId,
                Settings = ParseJsonMap(settings),
                RunId = runGuid,
                SupersedesId = supersedesGuid,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.AnalysisArtifacts.Add(analysis);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                analysis_id = analysis.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Create an asset set (bundle)")]
    public static async Task<string> CreateAssetSet(
        VectorDbContext dbContext,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Chapter id (optional)")] string? chapterId = null,
        [Description("Segment label (optional)")] string? segmentLabel = null,
        [Description("Subject id (optional)")] string? subjectId = null,
        [Description("Scene id (optional)")] string? sceneId = null,
        [Description("Label (optional)")] string? label = null,
        [Description("Set type (image_bundle, actorcards, start_images, layer_bundle, etc.)")] string? setType = null,
        [Description("Variant (training, start_image, prod.final, etc.)")] string? variant = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            var set = new AssetSet
            {
                StoryId = storyId,
                TimelineId = timelineId,
                ChapterId = chapterId,
                SegmentLabel = segmentLabel,
                SubjectId = subjectId,
                SceneId = sceneId,
                Label = label,
                SetType = setType,
                Variant = variant,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.AssetSets.Add(set);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                set_id = set.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Attach an artifact to an asset set")]
    public static async Task<string> AddAssetToSet(
        VectorDbContext dbContext,
        [Description("Asset set id")] string setId,
        [Description("Artifact id")] string artifactId,
        [Description("Role (image, mask, caption, etc.)")] string? role = null,
        [Description("Ordinal (optional)")] int? ordinal = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            if (!Guid.TryParse(setId, out var setGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid set_id format" });
            }
            if (!Guid.TryParse(artifactId, out var artifactGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid artifact_id format" });
            }

            var item = new AssetSetItem
            {
                SetId = setGuid,
                ArtifactId = artifactGuid,
                Role = role,
                Ordinal = ordinal,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.AssetSetItems.Add(item);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                asset_set_item_id = item.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Link a subject to an asset set")]
    public static async Task<string> LinkSubjectAssetSet(
        VectorDbContext dbContext,
        [Description("Subject id")] string subjectId,
        [Description("Asset set id")] string setId,
        [Description("Variant (optional)")] string? variant = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            if (!Guid.TryParse(setId, out var setGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid set_id format" });
            }

            var link = new SubjectAssetLink
            {
                SubjectId = subjectId,
                SetId = setGuid,
                Variant = variant,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.SubjectAssetLinks.Add(link);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                subject_asset_link_id = link.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Attach a layer asset set to a subject/scene/shot")]
    public static async Task<string> LinkLayer(
        VectorDbContext dbContext,
        [Description("Owner kind (subject|scene|shot)")] string ownerKind,
        [Description("Owner id")] string ownerId,
        [Description("Asset set id")] string setId,
        [Description("Layer type (ui|vfx|grade)")] string? layerType = null,
        [Description("Role (hud, title_card, lightning, etc.)")] string? role = null,
        [Description("Scope (actor_pov, scene_global, shot_global)")] string? scope = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            if (!Guid.TryParse(setId, out var setGuid))
            {
                return JsonSerializer.Serialize(new { success = false, error = "Invalid set_id format" });
            }

            var link = new LayerLink
            {
                OwnerKind = ownerKind,
                OwnerId = ownerId,
                SetId = setGuid,
                LayerType = layerType,
                Role = role,
                Scope = scope,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.LayerLinks.Add(link);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new
            {
                success = true,
                layer_link_id = link.Id
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Create or update a subject record")]
    public static async Task<string> UpsertSubject(
        VectorDbContext dbContext,
        [Description("Subject id")] string subjectId,
        [Description("Subject name")] string name,
        [Description("Subject type (optional)")] string? subjectType = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            var existing = await dbContext.Subjects.FirstOrDefaultAsync(s => s.Id == subjectId);
            if (existing == null)
            {
                var subject = new SubjectRecord
                {
                    Id = subjectId,
                    Name = name,
                    SubjectType = subjectType,
                    Metadata = ParseJsonMap(metadata)
                };
                dbContext.Subjects.Add(subject);
                await dbContext.SaveChangesAsync();

                return JsonSerializer.Serialize(new { success = true, subject_id = subject.Id, created = true });
            }

            existing.Name = name;
            existing.SubjectType = subjectType;
            existing.Metadata = ParseJsonMap(metadata);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new { success = true, subject_id = existing.Id, created = false });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Store a subject occurrence record")]
    public static async Task<string> StoreSubjectOccurrence(
        VectorDbContext dbContext,
        [Description("Subject id")] string subjectId,
        [Description("Source id (optional)")] string? sourceId = null,
        [Description("Chapter (optional)")] string? chapter = null,
        [Description("Segment label (optional)")] string? segmentLabel = null,
        [Description("Segment type (optional)")] string? segmentType = null,
        [Description("Phase id (optional)")] string? phaseId = null,
        [Description("Scene label (optional)")] string? sceneLabel = null,
        [Description("Metadata JSON (optional)")] string? metadata = null)
    {
        try
        {
            var occurrence = new SubjectOccurrence
            {
                SubjectId = subjectId,
                SourceId = sourceId,
                Chapter = chapter,
                SegmentLabel = segmentLabel,
                SegmentType = segmentType,
                PhaseId = phaseId,
                SceneLabel = sceneLabel,
                Metadata = ParseJsonMap(metadata)
            };

            dbContext.SubjectOccurrences.Add(occurrence);
            await dbContext.SaveChangesAsync();

            return JsonSerializer.Serialize(new { success = true, occurrence_id = occurrence.Id });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
    }

    [McpServerTool]
    [Description("Fetch asset sets and artifacts for a segment using Qdrant filter + canonical store")]
    public static async Task<string> GetAssetsBySegment(
        VectorDbContext dbContext,
        VectorStoreSettings settings,
        [Description("Qdrant collection to scroll")] string collection,
        [Description("Chapter id (required unless filterJson is provided)")] string? chapterId = null,
        [Description("Segment label (required unless filterJson is provided)")] string? segmentLabel = null,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Scene id (optional)")] string? sceneId = null,
        [Description("Phase id (optional)")] string? phaseId = null,
        [Description("Qdrant filter JSON override (optional)")] string? filterJson = null,
        [Description("Max points to scan (default: 500)")] int limit = 500,
        [Description("Fallback to Postgres if Qdrant yields no IDs (default: true)")] bool fallbackToPostgres = true)
    {
        JsonDocument? filterDoc = null;
        try
        {
            if (string.IsNullOrWhiteSpace(filterJson))
            {
                if (string.IsNullOrWhiteSpace(chapterId) || string.IsNullOrWhiteSpace(segmentLabel))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "chapterId and segmentLabel are required when filterJson is not provided" });
                }
            }

            object filterPayload;
            if (!string.IsNullOrWhiteSpace(filterJson))
            {
                filterDoc = JsonDocument.Parse(filterJson);
                filterPayload = filterDoc.RootElement;
            }
            else
            {
                filterPayload = BuildSegmentFilter(
                    chapterId ?? string.Empty,
                    segmentLabel ?? string.Empty,
                    storyId,
                    timelineId,
                    sceneId,
                    phaseId
                );
            }

            var points = await ScrollQdrantPointsAsync(settings, collection, filterPayload, limit);
            var setIds = new HashSet<Guid>();
            var artifactIds = new HashSet<Guid>();

            foreach (var point in points)
            {
                if (point.TryGetProperty("payload", out var payloadElement))
                {
                    CollectAssetIds(payloadElement, setIds, artifactIds);
                }
            }

            var assetSets = new List<AssetSet>();
            var usedFallback = false;

            if (setIds.Count > 0)
            {
                assetSets = await dbContext.AssetSets
                    .AsNoTracking()
                    .Where(set => setIds.Contains(set.Id))
                    .ToListAsync();
            }
            else if (fallbackToPostgres)
            {
                usedFallback = true;
                var query = dbContext.AssetSets.AsNoTracking().AsQueryable();

                if (!string.IsNullOrWhiteSpace(storyId))
                {
                    query = query.Where(set => set.StoryId == storyId);
                }

                if (!string.IsNullOrWhiteSpace(timelineId))
                {
                    query = query.Where(set => set.TimelineId == timelineId);
                }

                if (!string.IsNullOrWhiteSpace(chapterId))
                {
                    query = query.Where(set => set.ChapterId == chapterId);
                }

                if (!string.IsNullOrWhiteSpace(segmentLabel))
                {
                    query = query.Where(set => set.SegmentLabel == segmentLabel);
                }

                if (!string.IsNullOrWhiteSpace(sceneId))
                {
                    query = query.Where(set => set.SceneId == sceneId);
                }

                assetSets = await query.ToListAsync();
                foreach (var set in assetSets)
                {
                    setIds.Add(set.Id);
                }
            }

            var setItems = new List<AssetSetItem>();
            if (setIds.Count > 0)
            {
                setItems = await dbContext.AssetSetItems
                    .AsNoTracking()
                    .Where(item => setIds.Contains(item.SetId))
                    .ToListAsync();
            }

            foreach (var item in setItems)
            {
                artifactIds.Add(item.ArtifactId);
            }

            var artifacts = new List<ArtifactRecord>();
            if (artifactIds.Count > 0)
            {
                artifacts = await dbContext.Artifacts
                    .AsNoTracking()
                    .Where(artifact => artifactIds.Contains(artifact.Id))
                    .ToListAsync();
            }

            var resolvedSetIds = assetSets.Select(set => set.Id).ToHashSet();
            var missingSetIds = setIds.Except(resolvedSetIds).Select(id => id.ToString()).ToList();
            var resolvedArtifactIds = artifacts.Select(artifact => artifact.Id).ToHashSet();
            var missingArtifactIds = artifactIds.Except(resolvedArtifactIds).Select(id => id.ToString()).ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                collection,
                qdrant_points = points.Count,
                set_id_count = setIds.Count,
                artifact_id_count = artifactIds.Count,
                fallback_used = usedFallback,
                missing_set_ids = missingSetIds,
                missing_artifact_ids = missingArtifactIds,
                asset_sets = assetSets.Select(set => new
                {
                    id = set.Id,
                    story_id = set.StoryId,
                    timeline_id = set.TimelineId,
                    chapter_id = set.ChapterId,
                    segment_label = set.SegmentLabel,
                    subject_id = set.SubjectId,
                    scene_id = set.SceneId,
                    label = set.Label,
                    set_type = set.SetType,
                    variant = set.Variant,
                    meta = set.Metadata,
                    created_at = set.CreatedAt
                }),
                asset_set_items = setItems.Select(item => new
                {
                    id = item.Id,
                    set_id = item.SetId,
                    artifact_id = item.ArtifactId,
                    role = item.Role,
                    ordinal = item.Ordinal,
                    meta = item.Metadata,
                    created_at = item.CreatedAt
                }),
                artifacts = artifacts.Select(artifact => new
                {
                    id = artifact.Id,
                    kind = artifact.Kind,
                    sha256 = artifact.Sha256,
                    content = artifact.Content,
                    storage_path = artifact.StoragePath,
                    mime = artifact.Mime,
                    size_bytes = artifact.SizeBytes,
                    run_id = artifact.RunId,
                    story_id = artifact.StoryId,
                    timeline_id = artifact.TimelineId,
                    unit_ref = artifact.UnitRef,
                    meta = artifact.Metadata,
                    created_at = artifact.CreatedAt
                })
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
        finally
        {
            filterDoc?.Dispose();
        }
    }

    [McpServerTool]
    [Description("Fetch subjects for a segment using Qdrant filter (exact scroll)")]
    public static async Task<string> GetSubjectsBySegment(
        VectorStoreSettings settings,
        [Description("Qdrant collection to scroll")] string collection,
        [Description("Chapter id (required unless filterJson is provided)")] string? chapterId = null,
        [Description("Segment label (required unless filterJson is provided)")] string? segmentLabel = null,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Scene id (optional)")] string? sceneId = null,
        [Description("Phase id (optional)")] string? phaseId = null,
        [Description("Subject type filter (optional)")] string? subjectType = null,
        [Description("Role filter (optional)")] string? role = null,
        [Description("Qdrant filter JSON override (optional)")] string? filterJson = null,
        [Description("Max points to scan (default: 1000)")] int limit = 1000)
    {
        JsonDocument? filterDoc = null;
        try
        {
            if (string.IsNullOrWhiteSpace(filterJson))
            {
                if (string.IsNullOrWhiteSpace(chapterId) || string.IsNullOrWhiteSpace(segmentLabel))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "chapterId and segmentLabel are required when filterJson is not provided" });
                }
            }

            object filterPayload;
            if (!string.IsNullOrWhiteSpace(filterJson))
            {
                filterDoc = JsonDocument.Parse(filterJson);
                filterPayload = filterDoc.RootElement;
            }
            else
            {
                filterPayload = BuildOccurrenceFilter(
                    chapterId ?? string.Empty,
                    segmentLabel ?? string.Empty,
                    storyId,
                    timelineId,
                    sceneId,
                    phaseId,
                    subjectType,
                    role
                );
            }

            var points = await ScrollQdrantPointsAsync(settings, collection, filterPayload, limit);
            var subjects = new Dictionary<string, SubjectSummary>(StringComparer.OrdinalIgnoreCase);
            var roleCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            var typeCounts = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            var totalOccurrences = 0;

            foreach (var point in points)
            {
                if (!point.TryGetProperty("payload", out var payloadElement))
                {
                    continue;
                }

                var subjectId = ReadPayloadString(payloadElement, "subject_id", "owner_id");
                if (string.IsNullOrWhiteSpace(subjectId))
                {
                    continue;
                }

                var subjectTypeValue = ReadPayloadString(payloadElement, "subject_type");
                var roles = ReadPayloadStringList(payloadElement, "roles");

                if (!subjects.TryGetValue(subjectId, out var summary))
                {
                    summary = new SubjectSummary(subjectId);
                    subjects[subjectId] = summary;
                }

                summary.Count += 1;
                if (!string.IsNullOrWhiteSpace(subjectTypeValue))
                {
                    summary.SubjectType = subjectTypeValue;
                }

                foreach (var roleValue in roles)
                {
                    summary.Roles.Add(roleValue);
                }

                totalOccurrences += 1;
            }

            foreach (var summary in subjects.Values)
            {
                if (!string.IsNullOrWhiteSpace(summary.SubjectType))
                {
                    typeCounts[summary.SubjectType] = typeCounts.TryGetValue(summary.SubjectType, out var count)
                        ? count + 1
                        : 1;
                }

                foreach (var roleValue in summary.Roles)
                {
                    roleCounts[roleValue] = roleCounts.TryGetValue(roleValue, out var count)
                        ? count + 1
                        : 1;
                }
            }

            var subjectList = subjects.Values
                .OrderByDescending(item => item.Count)
                .Select(item => new
                {
                    subject_id = item.SubjectId,
                    subject_type = item.SubjectType,
                    roles = item.Roles.OrderBy(r => r).ToList(),
                    occurrence_count = item.Count
                })
                .ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                collection,
                total_occurrences = totalOccurrences,
                subjects = subjectList,
                subject_type_counts = typeCounts,
                role_counts = roleCounts
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
        finally
        {
            filterDoc?.Dispose();
        }
    }

    [McpServerTool]
    [Description("List segment labels for a chapter using Qdrant filter (exact scroll)")]
    public static async Task<string> GetSegmentsByChapter(
        VectorStoreSettings settings,
        [Description("Qdrant collection to scroll")] string collection,
        [Description("Chapter id (required unless filterJson is provided)")] string? chapterId = null,
        [Description("Story id (optional)")] string? storyId = null,
        [Description("Timeline id (optional)")] string? timelineId = null,
        [Description("Qdrant filter JSON override (optional)")] string? filterJson = null,
        [Description("Max points to scan (default: 5000)")] int limit = 5000)
    {
        JsonDocument? filterDoc = null;
        try
        {
            if (string.IsNullOrWhiteSpace(filterJson))
            {
                if (string.IsNullOrWhiteSpace(chapterId))
                {
                    return JsonSerializer.Serialize(new { success = false, error = "chapterId is required when filterJson is not provided" });
                }
            }

            object filterPayload;
            if (!string.IsNullOrWhiteSpace(filterJson))
            {
                filterDoc = JsonDocument.Parse(filterJson);
                filterPayload = filterDoc.RootElement;
            }
            else
            {
                filterPayload = BuildOccurrenceFilter(
                    chapterId ?? string.Empty,
                    segmentLabel: null,
                    storyId: storyId,
                    timelineId: timelineId,
                    sceneId: null,
                    phaseId: null,
                    subjectType: null,
                    role: null
                );
            }

            var points = await ScrollQdrantPointsAsync(settings, collection, filterPayload, limit);
            var segments = new Dictionary<string, SegmentSummary>(StringComparer.OrdinalIgnoreCase);

            foreach (var point in points)
            {
                if (!point.TryGetProperty("payload", out var payloadElement))
                {
                    continue;
                }

                var segmentLabel = ReadPayloadString(payloadElement, "segment_label");
                if (string.IsNullOrWhiteSpace(segmentLabel))
                {
                    continue;
                }

                var segmentType = ReadPayloadString(payloadElement, "segment_type");
                var sceneLabel = ReadPayloadString(payloadElement, "scene_label", "scene_id");

                if (!segments.TryGetValue(segmentLabel, out var summary))
                {
                    summary = new SegmentSummary(segmentLabel);
                    segments[segmentLabel] = summary;
                }

                summary.Count += 1;
                if (!string.IsNullOrWhiteSpace(segmentType))
                {
                    summary.SegmentType = segmentType;
                }
                if (!string.IsNullOrWhiteSpace(sceneLabel))
                {
                    summary.SceneLabels.Add(sceneLabel);
                }
            }

            var segmentList = segments.Values
                .OrderBy(item => item.SegmentLabel, StringComparer.OrdinalIgnoreCase)
                .Select(item => new
                {
                    segment_label = item.SegmentLabel,
                    segment_type = item.SegmentType,
                    occurrence_count = item.Count,
                    scene_labels = item.SceneLabels.OrderBy(s => s).ToList()
                })
                .ToList();

            return JsonSerializer.Serialize(new
            {
                success = true,
                collection,
                segments = segmentList,
                segment_count = segmentList.Count
            });
        }
        catch (Exception ex)
        {
            return SerializeError(ex);
        }
        finally
        {
            filterDoc?.Dispose();
        }
    }

    private static Dictionary<string, object> BuildSegmentFilter(
        string chapterId,
        string segmentLabel,
        string? storyId,
        string? timelineId,
        string? sceneId,
        string? phaseId)
    {
        var must = new List<Dictionary<string, object>>();
        AddMatch(must, "chapter_id", chapterId);
        AddMatch(must, "segment_label", segmentLabel);
        AddMatch(must, "story_id", storyId);
        AddMatch(must, "timeline_id", timelineId);
        AddMatch(must, "scene_id", sceneId);
        AddMatch(must, "phase_id", phaseId);

        return new Dictionary<string, object>
        {
            ["must"] = must
        };
    }

    private static Dictionary<string, object> BuildOccurrenceFilter(
        string chapterId,
        string? segmentLabel,
        string? storyId,
        string? timelineId,
        string? sceneId,
        string? phaseId,
        string? subjectType,
        string? role)
    {
        var must = new List<Dictionary<string, object>>();
        AddMatch(must, "doc_kind", "occurrence");
        AddMatch(must, "chapter_id", chapterId);
        AddMatch(must, "segment_label", segmentLabel);
        AddMatch(must, "story_id", storyId);
        AddMatch(must, "timeline_id", timelineId);
        AddMatch(must, "scene_id", sceneId);
        AddMatch(must, "phase_id", phaseId);
        AddMatch(must, "subject_type", subjectType);
        AddMatch(must, "roles", role);

        return new Dictionary<string, object>
        {
            ["must"] = must
        };
    }

    private static void AddMatch(List<Dictionary<string, object>> must, string key, string? value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            return;
        }

        must.Add(new Dictionary<string, object>
        {
            ["key"] = key,
            ["match"] = new Dictionary<string, object> { ["value"] = value }
        });
    }

    private static async Task<List<JsonElement>> ScrollQdrantPointsAsync(
        VectorStoreSettings settings,
        string collection,
        object filterPayload,
        int limit)
    {
        var qdrantUrl = $"http://{settings.QdrantHost}:{settings.QdrantHttpPort}/collections/{collection}/points/scroll";
        var results = new List<JsonElement>();
        var remaining = limit > 0 ? limit : int.MaxValue;
        object? offset = null;

        using var http = new HttpClient();

        while (remaining > 0)
        {
            var pageSize = Math.Min(remaining, 256);
            var payload = new Dictionary<string, object>
            {
                ["limit"] = pageSize,
                ["with_payload"] = true,
                ["with_vectors"] = false,
                ["filter"] = filterPayload
            };

            if (offset != null)
            {
                payload["offset"] = offset;
            }

            var requestBody = JsonSerializer.Serialize(payload);
            using var response = await http.PostAsync(qdrantUrl, new StringContent(requestBody, Encoding.UTF8, "application/json"));
            var responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new InvalidOperationException($"Qdrant scroll failed: {responseBody}");
            }

            using var doc = JsonDocument.Parse(responseBody);
            if (!doc.RootElement.TryGetProperty("result", out var resultElement))
            {
                break;
            }

            if (resultElement.TryGetProperty("points", out var pointsElement) && pointsElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var point in pointsElement.EnumerateArray())
                {
                    results.Add(point);
                    remaining -= 1;
                    if (remaining <= 0)
                    {
                        break;
                    }
                }
            }

            offset = null;
            if (remaining > 0 && resultElement.TryGetProperty("next_page_offset", out var offsetElement))
            {
                if (offsetElement.ValueKind == JsonValueKind.String)
                {
                    offset = offsetElement.GetString();
                }
                else if (offsetElement.ValueKind == JsonValueKind.Number && offsetElement.TryGetInt64(out var offsetNumber))
                {
                    offset = offsetNumber;
                }
                else if (offsetElement.ValueKind != JsonValueKind.Null && offsetElement.ValueKind != JsonValueKind.Undefined)
                {
                    offset = offsetElement.GetRawText();
                }
            }

            if (offset == null)
            {
                break;
            }
        }

        return results;
    }

    private static void CollectAssetIds(JsonElement payloadElement, HashSet<Guid> setIds, HashSet<Guid> artifactIds)
    {
        AddGuidFromPayload(payloadElement, "set_id", setIds);
        AddGuidFromPayload(payloadElement, "asset_set_id", setIds);
        AddGuidFromPayload(payloadElement, "set_ids", setIds);

        AddGuidFromPayload(payloadElement, "artifact_id", artifactIds);
        AddGuidFromPayload(payloadElement, "artifact_ids", artifactIds);
        AddGuidFromPayload(payloadElement, "asset_id", artifactIds);
    }

    private static void AddGuidFromPayload(JsonElement payloadElement, string key, HashSet<Guid> target)
    {
        if (!payloadElement.TryGetProperty(key, out var value))
        {
            return;
        }

        if (value.ValueKind == JsonValueKind.Array)
        {
            foreach (var entry in value.EnumerateArray())
            {
                AddGuidValue(entry, target);
            }
            return;
        }

        AddGuidValue(value, target);
    }

    private static void AddGuidValue(JsonElement value, HashSet<Guid> target)
    {
        var text = value.ValueKind == JsonValueKind.String ? value.GetString() : value.ToString();
        if (!string.IsNullOrWhiteSpace(text) && Guid.TryParse(text, out var guid))
        {
            target.Add(guid);
        }
    }

    private static string? ReadPayloadString(JsonElement payloadElement, params string[] keys)
    {
        foreach (var key in keys)
        {
            if (!payloadElement.TryGetProperty(key, out var value))
            {
                continue;
            }

            if (value.ValueKind == JsonValueKind.String)
            {
                var text = value.GetString();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    return text;
                }
                continue;
            }

            if (value.ValueKind == JsonValueKind.Number || value.ValueKind == JsonValueKind.True || value.ValueKind == JsonValueKind.False)
            {
                return value.ToString();
            }
        }

        return null;
    }

    private static List<string> ReadPayloadStringList(JsonElement payloadElement, string key)
    {
        var results = new List<string>();
        if (!payloadElement.TryGetProperty(key, out var value))
        {
            return results;
        }

        if (value.ValueKind == JsonValueKind.Array)
        {
            foreach (var entry in value.EnumerateArray())
            {
                var text = entry.ValueKind == JsonValueKind.String ? entry.GetString() : entry.ToString();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    results.Add(text);
                }
            }

            return results;
        }

        var single = value.ValueKind == JsonValueKind.String ? value.GetString() : value.ToString();
        if (!string.IsNullOrWhiteSpace(single))
        {
            results.Add(single);
        }

        return results;
    }

    private sealed class SubjectSummary
    {
        public SubjectSummary(string subjectId)
        {
            SubjectId = subjectId;
        }

        public string SubjectId { get; }
        public string? SubjectType { get; set; }
        public HashSet<string> Roles { get; } = new(StringComparer.OrdinalIgnoreCase);
        public int Count { get; set; }
    }

    private sealed class SegmentSummary
    {
        public SegmentSummary(string segmentLabel)
        {
            SegmentLabel = segmentLabel;
        }

        public string SegmentLabel { get; }
        public string? SegmentType { get; set; }
        public HashSet<string> SceneLabels { get; } = new(StringComparer.OrdinalIgnoreCase);
        public int Count { get; set; }
    }

    private static Dictionary<string, object> ParseJsonMap(string? json)
    {
        if (string.IsNullOrWhiteSpace(json))
        {
            return new Dictionary<string, object>();
        }

        try
        {
            var parsed = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
            return parsed ?? new Dictionary<string, object>();
        }
        catch (JsonException)
        {
            return new Dictionary<string, object> { ["metadata_error"] = "Invalid JSON format" };
        }
    }

    private static string SerializeError(Exception ex)
    {
        Console.Error.WriteLine($"[CanonicalTools] {ex.GetType().FullName}: {ex.Message}");
        if (ex.InnerException != null)
        {
            Console.Error.WriteLine($"[CanonicalTools] Inner: {ex.InnerException.GetType().FullName}: {ex.InnerException.Message}");
        }

        var payload = new Dictionary<string, object?>
        {
            ["success"] = false,
            ["error"] = ex.Message,
            ["error_type"] = ex.GetType().FullName
        };

        if (ex.InnerException != null)
        {
            payload["inner_error"] = ex.InnerException.Message;
            payload["inner_error_type"] = ex.InnerException.GetType().FullName;
        }

        if (ex is DbUpdateException dbUpdateException && dbUpdateException.InnerException != null)
        {
            payload["db_error"] = dbUpdateException.InnerException.Message;
        }

        return JsonSerializer.Serialize(payload);
    }
}
