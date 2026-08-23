using Microsoft.EntityFrameworkCore;

namespace VectorMcpServer.Data;

public static class SchemaBootstrapper
{
    public static async Task EnsureSchemaAsync(VectorDbContext dbContext)
    {
        var statements = new[]
        {
            "CREATE TABLE IF NOT EXISTS runs (" +
            "id uuid PRIMARY KEY, " +
            "run_type text NOT NULL, " +
            "story_id text, " +
            "timeline_id text, " +
            "unit_ref text, " +
            "input_sha256 text, " +
            "prompt_bundle_sha text, " +
            "model_id text, " +
            "settings jsonb, " +
            "inputs jsonb, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS artifacts (" +
            "id uuid PRIMARY KEY, " +
            "kind text NOT NULL, " +
            "sha256 text, " +
            "content text, " +
            "storage_path text, " +
            "mime text, " +
            "size_bytes bigint, " +
            "run_id uuid REFERENCES runs(id) ON DELETE SET NULL, " +
            "story_id text, " +
            "timeline_id text, " +
            "unit_ref text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS run_outputs (" +
            "id uuid PRIMARY KEY, " +
            "run_id uuid NOT NULL REFERENCES runs(id) ON DELETE CASCADE, " +
            "artifact_id uuid NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE, " +
            "role text NOT NULL, " +
            "ordinal integer, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS text_units (" +
            "id uuid PRIMARY KEY, " +
            "unit_ref text NOT NULL, " +
            "story_id text, " +
            "timeline_id text, " +
            "chapter_id text, " +
            "segment_label text, " +
            "segment_type text, " +
            "verse_id text, " +
            "scene_id text, " +
            "content text NOT NULL, " +
            "sha256 text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS analysis_artifacts (" +
            "id uuid PRIMARY KEY, " +
            "text_unit_id uuid REFERENCES text_units(id) ON DELETE SET NULL, " +
            "analysis_type text, " +
            "artifact_id uuid REFERENCES artifacts(id) ON DELETE SET NULL, " +
            "content text, " +
            "sha256 text, " +
            "prompt_bundle_sha text, " +
            "model_id text, " +
            "settings jsonb, " +
            "run_id uuid REFERENCES runs(id) ON DELETE SET NULL, " +
            "supersedes_id uuid REFERENCES analysis_artifacts(id) ON DELETE SET NULL, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS asset_sets (" +
            "id uuid PRIMARY KEY, " +
            "story_id text, " +
            "timeline_id text, " +
            "chapter_id text, " +
            "segment_label text, " +
            "subject_id text, " +
            "scene_id text, " +
            "label text, " +
            "set_type text, " +
            "variant text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS asset_set_items (" +
            "id uuid PRIMARY KEY, " +
            "set_id uuid NOT NULL REFERENCES asset_sets(id) ON DELETE CASCADE, " +
            "artifact_id uuid NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE, " +
            "role text, " +
            "ordinal integer, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS subjects (" +
            "id text PRIMARY KEY, " +
            "name text NOT NULL, " +
            "subject_type text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS subject_occurrences (" +
            "id uuid PRIMARY KEY, " +
            "subject_id text NOT NULL REFERENCES subjects(id) ON DELETE CASCADE, " +
            "source_id text, " +
            "chapter text, " +
            "segment_label text, " +
            "segment_type text, " +
            "phase_id text, " +
            "scene_label text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "ALTER TABLE subject_occurrences ADD COLUMN IF NOT EXISTS phase_id text;",
            "CREATE TABLE IF NOT EXISTS subject_asset_links (" +
            "id uuid PRIMARY KEY, " +
            "subject_id text NOT NULL REFERENCES subjects(id) ON DELETE CASCADE, " +
            "set_id uuid NOT NULL REFERENCES asset_sets(id) ON DELETE CASCADE, " +
            "variant text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS layer_links (" +
            "id uuid PRIMARY KEY, " +
            "owner_kind text NOT NULL, " +
            "owner_id text NOT NULL, " +
            "set_id uuid NOT NULL REFERENCES asset_sets(id) ON DELETE CASCADE, " +
            "layer_type text, " +
            "role text, " +
            "scope text, " +
            "meta jsonb, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE TABLE IF NOT EXISTS engram_index (" +
            "id uuid PRIMARY KEY, " +
            "document_id uuid NOT NULL REFERENCES vector_documents(id) ON DELETE CASCADE, " +
            "collection text, " +
            "layer_id integer NOT NULL, " +
            "hashes bigint[] NOT NULL, " +
            "token_count integer, " +
            "created_at timestamptz DEFAULT now()" +
            ");",
            "CREATE INDEX IF NOT EXISTS idx_runs_type ON runs(run_type);",
            "CREATE INDEX IF NOT EXISTS idx_runs_story ON runs(story_id);",
            "CREATE INDEX IF NOT EXISTS idx_runs_timeline ON runs(timeline_id);",
            "CREATE INDEX IF NOT EXISTS idx_runs_unit_ref ON runs(unit_ref);",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_kind ON artifacts(kind);",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_sha ON artifacts(sha256);",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_story ON artifacts(story_id);",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_timeline ON artifacts(timeline_id);",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_unit_ref ON artifacts(unit_ref);",
            "CREATE INDEX IF NOT EXISTS idx_run_outputs_run ON run_outputs(run_id);",
            "CREATE INDEX IF NOT EXISTS idx_run_outputs_artifact ON run_outputs(artifact_id);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_unit_ref ON text_units(unit_ref);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_story ON text_units(story_id);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_timeline ON text_units(timeline_id);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_chapter ON text_units(chapter_id);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_segment ON text_units(segment_label);",
            "CREATE INDEX IF NOT EXISTS idx_text_units_scene ON text_units(scene_id);",
            "CREATE INDEX IF NOT EXISTS idx_analysis_artifacts_unit ON analysis_artifacts(text_unit_id);",
            "CREATE INDEX IF NOT EXISTS idx_analysis_artifacts_type ON analysis_artifacts(analysis_type);",
            "CREATE INDEX IF NOT EXISTS idx_analysis_artifacts_run ON analysis_artifacts(run_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_sets_story ON asset_sets(story_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_sets_timeline ON asset_sets(timeline_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_sets_subject ON asset_sets(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_sets_scene ON asset_sets(scene_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_set_items_set ON asset_set_items(set_id);",
            "CREATE INDEX IF NOT EXISTS idx_asset_set_items_artifact ON asset_set_items(artifact_id);",
            "CREATE INDEX IF NOT EXISTS idx_subjects_type ON subjects(subject_type);",
            "CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name);",
            "CREATE INDEX IF NOT EXISTS idx_subject_occurrences_subject ON subject_occurrences(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_subject_occurrences_chapter ON subject_occurrences(chapter);",
            "CREATE INDEX IF NOT EXISTS idx_subject_occurrences_phase ON subject_occurrences(phase_id);",
            "CREATE INDEX IF NOT EXISTS idx_subject_asset_links_subject ON subject_asset_links(subject_id);",
            "CREATE INDEX IF NOT EXISTS idx_subject_asset_links_set ON subject_asset_links(set_id);",
            "CREATE INDEX IF NOT EXISTS idx_layer_links_owner_kind ON layer_links(owner_kind);",
            "CREATE INDEX IF NOT EXISTS idx_layer_links_owner_id ON layer_links(owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_layer_links_set ON layer_links(set_id);",
            "CREATE INDEX IF NOT EXISTS idx_engram_index_document ON engram_index(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_engram_index_collection ON engram_index(collection);",
            "CREATE INDEX IF NOT EXISTS idx_engram_index_layer ON engram_index(layer_id);",
            "CREATE INDEX IF NOT EXISTS idx_engram_index_hashes ON engram_index USING GIN (hashes);"
        };

        foreach (var statement in statements)
        {
            await dbContext.Database.ExecuteSqlRawAsync(statement);
        }
    }
}
