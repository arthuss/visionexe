param(
    [switch]$Force,
    [string]$QdrantConfig = "",
    [string]$CollectionSuffix = "subjects",
    [string]$VenvPath = "knowledge_base/.venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Legacy script: knowledge_base registry reset was removed." -ForegroundColor Yellow
Write-Host "Use the exevision drop-in for vector storage (engine/tools/exevision)." -ForegroundColor Yellow
exit 1
