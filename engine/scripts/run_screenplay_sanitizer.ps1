param (
    [int]$Start = 1,
    [int]$End = 108,
    [switch]$DryRun,
    [string]$Output = "",
    [string]$StoryRoot = "",
    [string]$StoryConfig = ""
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot
Set-Location -Path $RepoRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

if ($StoryConfig) {
    $StoryConfigPath = (Resolve-Path -LiteralPath $StoryConfig).Path
} else {
    if (-not $StoryRoot) {
        $engineConfigPath = Join-Path $RepoRoot "engine\\config\\engine_config.json"
        $engineConfig = Get-Content -Path $engineConfigPath -Raw | ConvertFrom-Json
        $StoryRoot = $engineConfig.default_story_root
    }
    if (-not [System.IO.Path]::IsPathRooted($StoryRoot)) {
        $StoryRoot = Join-Path $RepoRoot $StoryRoot
    }
    $StoryConfigPath = Join-Path $StoryRoot "config\\story_config.json"
}

if (-not (Test-Path -LiteralPath $StoryConfigPath)) {
    Write-Host "FEHLER: story_config.json nicht gefunden: $StoryConfigPath" -ForegroundColor Red
    exit 1
}

$sanitizeScript = Join-Path $RepoRoot "engine\\workers\\screenplay_sanitizer.py"
$sanitizeArgs = @($sanitizeScript, "--story-config", $StoryConfigPath, "--start", $Start, "--end", $End)
if ($DryRun) { $sanitizeArgs += "--dry-run" }
if ($Output) { $sanitizeArgs += @("--output", $Output) }

python @sanitizeArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "Sanitizer fehlgeschlagen." -ForegroundColor Red
    exit 1
}
