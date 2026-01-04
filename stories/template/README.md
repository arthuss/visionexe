# Story Template

This folder is a starting point for a new story.

- Filmsets layout: `chapter_###/segment_###/scene_###/timeline_##/`
- Subjects live in `subjects/` (registry, profiles, occurrences)

Bootstrap filmsets from Ge'ez JSONL:

```
python engine/workers/setup_filmsets_from_geez.py --story-root stories/template --include-chapter-text
```
