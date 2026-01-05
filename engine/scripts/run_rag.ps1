param(
    [int]$Chapter = 1,
    [string]$Query = "",
    [switch]$Reindex,
    [string]$Config = "rag_config.json"
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot
Set-Location -Path $RepoRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

$chapterArg = $Chapter.ToString()
$configPath = ""
if ($Config) {
    if ([System.IO.Path]::IsPathRooted($Config)) {
        $configPath = $Config
    } else {
        $configPath = Join-Path $RepoRoot $Config
    }
    if (-not (Test-Path -LiteralPath $configPath)) {
        $configPath = ""
    }
}

$ragIndexer = Join-Path $RepoRoot "engine\\workers\\rag_indexer.py"
$ragQuery = Join-Path $RepoRoot "engine\\workers\\rag_query.py"

if ($Reindex) {
    Write-Host "Indexing chapter $chapterArg..." -ForegroundColor Cyan
    $indexArgs = @($ragIndexer, "--chapter", $chapterArg)
    if ($configPath) { $indexArgs += @("--config", $configPath) }
    python @indexArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Indexing failed." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

if (-not $Query) {
    $Query = "checklist status for this chapter"
}

Write-Host "Query: $Query" -ForegroundColor Yellow
$queryArgs = @($ragQuery, $Query, "--chapter", $chapterArg)
if ($configPath) { $queryArgs += @("--config", $configPath) }
python @queryArgs
