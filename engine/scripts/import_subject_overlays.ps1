param(
    [string[]]$OverlayPath = @("stories/template/subjects/timelines/timeline_01/overlays.jsonl"),
    [string]$TimelineId = "",
    [string]$VenvPath = "knowledge_base/.venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Legacy script: knowledge_base overlay imports were removed." -ForegroundColor Yellow
Write-Host "Use the exevision drop-in for vector storage (engine/tools/exevision)." -ForegroundColor Yellow
exit 1
