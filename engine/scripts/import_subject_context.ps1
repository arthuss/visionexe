param(
    [string]$OccurrencesPath = "",
    [string]$ScenesPath = "",
    [string]$EnvironmentRoutePath = "",
    [string]$DynamicSubjectsPath = "",
    [switch]$Truncate,
    [string]$VenvPath = "knowledge_base/.venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Legacy script: knowledge_base context imports were removed." -ForegroundColor Yellow
Write-Host "Use the exevision drop-in for vector storage (engine/tools/exevision)." -ForegroundColor Yellow
exit 1
