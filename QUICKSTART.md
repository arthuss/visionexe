# QUICKSTART

Dieses Dokument beschreibt die bevorzugte, praxisnahe Reihenfolge der Pipeline. Fokus: schnell starten, reproduzierbar bleiben, und moeglichst immer ueber die Skripte (PS1) arbeiten statt einzelne Python-Worker manuell aufzurufen.

Grundannahme:
- `docs/ethiopic_1enoch_p` enthaelt alle 108 Kapitel (chapter_001.txt ... chapter_108.txt).
- Story-Template ist `stories/template`.
- Du willst genau eine Timeline + ein Genre + einen Style als Stellschraube auswaehlen.

## 0) Vorbereitungen (Konfig)

Stelle sicher, dass `stories/template/config/story_config.json` die Defaults hat:
- `timeline_default` (z.B. `timeline_01`)
- `genre_profile` (eine Datei aus `stories/template/config/genre`)
- `style_profiles` (array mit einer Datei aus `stories/template/config/styles`)
- `mechanism_profile` (optional, Default: `config/timelines/rule_of_machanism.json`)
- `tone_dials` (Feinsteuerung, optional)

Beispiel (sinngemaess):

```json
{
  "timeline_default": "timeline_01",
  "genre_profile": "stories/template/config/genre/drama.json",
  "style_profiles": [
    "stories/template/config/styles/cinematiclook_filmlook.json"
  ],
  "tone_dials": {
    "pacing": "fast",
    "dialogue_density": "low",
    "darkness": "dark"
  }
}
```

## 1) Filmsets scaffolden (Pflicht)

Erstellt die Grundstruktur unter `filmsets/` aus den Ge'ez-Texten.

```powershell
python engine/workers/setup_filmsets_from_geez.py --story-root stories/template --include-chapter-text
```

## 2) Linguistic Quad Worker (Pflicht)

Der Orchestrator ist die Standard-Art, die A-D Layer und die L-Hauptanalyse zu fahren.
Skript: `engine/scripts/Linguistic_quad_worker.ps1`.

Minimal:

```powershell
powershell -File engine/scripts/Linguistic_quad_worker.ps1 -StoryConfig stories/template/config/story_config.json
```

Wichtige Control-Optionen in `stories/template/data/analysis/analysis_orchestrator_control.json`:
- `analysis_scope`: `chapter` | `chapter-batch` | `segment`
- `mode`: `pipeline-parallel` oder `stage-parallel`
- `max_parallel_chapters`, `max_parallel_calls`
- `stage_slot_limits` (z.B. L/H/S/M/G)
- `auto_self_heal`, `auto_self_heal_mode`, `self_heal_verse_root`
- `use_vertex`, `vertex_model`, `vertex_project`, `vertex_location`
- `log_root` fuer per-job Logs

Beispiel mit Self-Heal + Chapter-Scope:

```powershell
# control file anpassen, dann starten
powershell -File engine/scripts/Linguistic_quad_worker.ps1 `
  -StoryConfig stories/template/config/story_config.json `
  -ControlPath stories/template/data/analysis/analysis_orchestrator_control.json
```

## 3) Segment-Integritaet (Optional)

Falls du Segmente regenerieren oder fehlende Ordner auffuellen willst:

```powershell
python engine/workers/segment_self_healer.py --story-config stories/template/config/story_config.json --refresh-existing
```

## 4) Subject Extraction + Asset Bible (entscheidender Schritt)

Die Asset Bible muss aus Fliesstexten entstehen (keine Tags/Stichpunkte). Ziel ist,
einen dichten, literarischen Kontext pro Subject zu schaffen, bevor du Assets trainierst.

Vector MCP (exevision drop-in, optional):
- Start/Loader Details: `engine/tools/exevision/QUICKSTART.md`.
- Minimal Start (Stack + MCP):

```powershell
powershell -File engine/tools/exevision/scripts/start_vector_stack.ps1
powershell -File engine/tools/exevision/scripts/run_mcp_server.ps1
```

Analysis-Master Flow (kompositionsstark, Asset Bible):
1) `subject_registry_builder.py`: baut die Subject-Registry (Namen, Phasen, Occurrences).
2) `subject_registry_validate.py`: Gemini prueft die Registry gegen die gesamte Story und schreibt `registry_merge_log.json`.
3) `subject_registry_normalizer.py`: wendet Merge/Rewrite an und bereinigt IDs + Aliase.
4) `asset_bible_builder.py`: erstellt Base JSON.
5) `asset_bible_enricher.py`: schreibt dichte, literarische Cards (ASSET_BIBLE.md / jsonl).

Beispiel (Analysis-Master):

```powershell
python engine/workers/subject_registry_builder.py --story-config stories/template/config/story_config.json --timeline timeline_01
python engine/workers/subject_registry_validate.py --story-config stories/template/config/story_config.json --model gemini-3-pro-preview
python engine/workers/subject_registry_normalizer.py --story-config stories/template/config/story_config.json
python engine/workers/asset_bible_builder.py --story-config stories/template/config/story_config.json --timeline timeline_01
python engine/workers/asset_bible_enricher.py --story-config stories/template/config/story_config.json --timeline timeline_01 --use-gemini --model gemini-3-pro-preview --types character,prop,requisite,set_environment,scene
```

Hinweis: Der Enricher filtert standardmaessig auf `character, prop, requisite, set_environment, scene`.
Wenn du alle Typen willst: `--types character,prop,requisite,set_environment,scene`.

Hinweis: Die alten Subject-Registry Import-Skripte basieren auf `knowledge_base` und sind damit Legacy.

## 5) Narration (neuer Haupttext)

`drehbuch_narration_worker.py` erzeugt `DREHBUCH_NARRATIV.md` pro Kapitel. Er nutzt
Story-Text + A-D Layer + L-Analyse + Timeline/Genre/Style.

```powershell
python engine/workers/drehbuch_narration_worker.py --story-config stories/template/config/story_config.json --chapter 1 --llm-profile lmstudio_local
```

## 6) Hollywood Drehbuch (Production Script)

Haupt-Worker: `drehbuch_gemini.py`. Fallback: `drehbuch.py`.

Einzelkapitel:

```powershell
python engine/workers/drehbuch_gemini.py 1 --story-config stories/template/config/story_config.json --timeline timeline_01
```

Batch:

```powershell
powershell -File engine/scripts/run_all_chapters_gemini.ps1 -Start 1 -End 5 -StoryConfig stories/template/config/story_config.json
```

Fallback (Copilot/Local):

```powershell
powershell -File engine/scripts/run_all_chapters.ps1 -Start 1 -End 5 -StoryConfig stories/template/config/story_config.json
```

## 7) Regie-Fixes + Scene Instructions

Wenn REGIE JSON fehlt oder neu geschrieben werden muss:

```powershell
powershell -File engine/scripts/run_regie_fix.ps1 -Start 1 -End 5 -StoryConfig stories/template/config/story_config.json
```

Scene Instruction Export:

```powershell
python engine/workers/scene_instruction_builder.py --story-config stories/template/config/story_config.json --chapter 1
```

## 8) RAG Index

Kapitelweise RAG:

```powershell
powershell -File engine/scripts/run_rag.ps1 -Chapter 1 -StoryConfig stories/template/config/story_config.json
```

Schneller Small-Index:

```powershell
powershell -File engine/scripts/run_rag_small.ps1 -Chapter 1 -StoryConfig stories/template/config/story_config.json
```

Lokaler Qwen3-VL Embedder (exevision drop-in):

```powershell
powershell -File engine/scripts/start_qwen_embedder.ps1 -ModelPath "engine/tools/exevision/Models/Qwen3-VL-Embedding-2B" -Port 8090
```
Hinweis: Die RAG-Worker erwarten ein OpenAI/Ollama-kompatibles Embedding API. Falls du den Qwen3-VL Embedder nutzt,
passe `rag_utils.py`/`rag_config_small.json` an oder nutze einen kompatiblen Endpoint.

## 9) Audio

Standard:

```powershell
powershell -File engine/scripts/run_audio_agent.ps1 -Chapter 1 -StoryConfig stories/template/config/story_config.json
```

## 10) Subject Images, LoRA, Posen, Startimages (Comfy)

Typischer Ablauf:
- Subject-Image Queue bauen
- Bilder generieren
- LoRA Training
- 360/Pose Varianten
- Startimages compositen

Skripte:

```powershell
powershell -File engine/scripts/run_subject_image_queue.ps1 -StoryConfig stories/template/config/story_config.json
powershell -File engine/scripts/run_chapter_timeline.ps1 -Chapter 1 -Timeline timeline_01 -Type image -StoryConfig stories/template/config/story_config.json
```

## 11) Video Generation (Comfy + LTX2)

Nach Startimages kannst du Video-Queues erzeugen und verteilen.
`run_chapter_timeline.ps1` kann `-Type video` oder `-Type all`.

```powershell
powershell -File engine/scripts/run_chapter_timeline.ps1 -Chapter 1 -Timeline timeline_01 -Type video -StoryConfig stories/template/config/story_config.json
```

## 12) Validator/Alternative Pipeline (optional)

`engine/run_pipeline.py` ist eine separate, tiefere Analyse-Pipeline (Morphologie/Syntax/Semantik)
mit optionalen Tests (Repro, Kontextfenster, Back-Translation). Nutze sie, wenn du die
linguistischen Artefakte strikt validieren willst.

Kurzform:

```powershell
python engine/run_pipeline.py --input docs/ethiopic_1enoch_p --outdir reports --use-gemini
```

## Script Index (ueberblick, keine Details)

Wichtige PS1 Wrapper:
- `engine/scripts/Linguistic_quad_worker.ps1` (A-D + L Analyse orchestrieren)
- `engine/scripts/run_all_chapters_gemini.ps1` / `run_all_chapters.ps1` (Drehbuch Batch)
- `engine/scripts/run_missing_chapters.ps1` (Repair-Flow)
- `engine/scripts/run_regie_fix.ps1` (REGIE JSON)
- `engine/scripts/run_scene_header_fixer.ps1` (Header Fix)
- `engine/scripts/run_screenplay_sanitizer.ps1` (Sanitize)
- `engine/scripts/run_rag.ps1` / `run_rag_small.ps1` / `run_rag_all.ps1`
- `engine/scripts/run_audio_agent.ps1`
- `engine/scripts/run_subject_image_queue.ps1`
- `engine/scripts/run_chapter_timeline.ps1`
- `engine/scripts/start_comfyui314wsl.ps1` (ComfyUI boot)
- `engine/scripts/start_diffusion_pipe.ps1` (lokaler Diffusions-Stack)
- `engine/scripts/start_scout_deck.ps1` (UI/monitor)

Wenn du fuer einen Schritt direkte Python-Worker brauchst, siehe `docs/workers.md`.
