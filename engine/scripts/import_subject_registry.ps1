param(
    [string]$StoryId = "template",
    [string]$TimelineId = "timeline_01",
    [string]$RegistryPath = "",
    [string]$ProfilesPath = "",
    [switch]$IncludeNotes,
    [string]$VenvPath = "knowledge_base/.venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Legacy script: knowledge_base subject imports were removed." -ForegroundColor Yellow
Write-Host "Use the exevision drop-in for vector storage (engine/tools/exevision)." -ForegroundColor Yellow
exit 1
