param(
    [switch]$QdrantSync,
    [string]$QdrantConfig = "engine/workers/rag_config_small.json",
    [string]$CollectionSuffix = "subjects",
    [string]$VenvPath = "knowledge_base/.venv"
)

$ErrorActionPreference = "Stop"

Write-Host "Legacy script: knowledge_base MCP server was removed." -ForegroundColor Yellow
Write-Host "Use engine/tools/exevision/scripts/run_mcp_server.ps1 instead." -ForegroundColor Yellow
exit 1
