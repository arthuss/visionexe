param(
    [Parameter(Mandatory = $true)]
    [string]$Chapter,
    [Parameter(Mandatory = $true)]
    [string]$Timeline,
    [ValidateSet("image", "video", "all")]
    [string]$Type = "image",
    [string]$Source = "",
    [bool]$ByScene = $true,
    [string]$ComfyUrl = "http://127.0.0.1:8188",
    [switch]$SkipGenerate,
    [switch]$SkipDistribute,
    [switch]$DryRun,
    [string]$StoryRoot = "",
    [string]$StoryConfig = ""
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$engineRoot = Split-Path -Parent $scriptRoot
$repoRoot = Split-Path -Parent $engineRoot
$root = $engineRoot
$python = (Get-Command python -ErrorAction Stop).Source
Set-Location -Path $repoRoot

if ($StoryConfig) {
    $StoryConfigPath = (Resolve-Path -LiteralPath $StoryConfig).Path
} else {
    if (-not $StoryRoot) {
        $engineConfigPath = Join-Path $repoRoot "engine\\config\\engine_config.json"
        $engineConfig = Get-Content -Path $engineConfigPath -Raw | ConvertFrom-Json
        $StoryRoot = $engineConfig.default_story_root
    }
    if (-not [System.IO.Path]::IsPathRooted($StoryRoot)) {
        $StoryRoot = Join-Path $repoRoot $StoryRoot
    }
    $StoryConfigPath = Join-Path $StoryRoot "config\\story_config.json"
}

if (-not (Test-Path -LiteralPath $StoryConfigPath)) {
    Write-Host "FEHLER: story_config.json nicht gefunden: $StoryConfigPath" -ForegroundColor Red
    exit 1
}

$storyConfig = Get-Content -Path $StoryConfigPath -Raw | ConvertFrom-Json
if (-not $Source) {
    $Source = $storyConfig.produced_assets_root
    if (-not [System.IO.Path]::IsPathRooted($Source)) {
        $Source = Join-Path $repoRoot $Source
    }
}

if (-not $SkipGenerate) {
    try {
        $uri = [uri]$ComfyUrl
        $port = if ($uri.Port -gt 0) { $uri.Port } else { 8188 }
        $conn = Test-NetConnection -ComputerName $uri.Host -Port $port -WarningAction SilentlyContinue
        if (-not $conn.TcpTestSucceeded) {
            Write-Host "ComfyUI not reachable at $ComfyUrl. Start ComfyUI or adjust --ComfyUrl." -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "ComfyUI check failed: $($_.Exception.Message)" -ForegroundColor Yellow
        exit 1
    }

    $genArgs = @(
        Join-Path $root "workers\\generate_chapter_assets.py",
        "--chapter", $Chapter,
        "--type", $Type,
        "--timeline", $Timeline,
        "--story-config", $StoryConfigPath
    )
    if ($DryRun) { $genArgs += "--dry-run" }
    & $python @genArgs
}

if (-not $SkipDistribute) {
    $distArgs = @(
        Join-Path $root "workers\\distribute_chapter_assets.py",
        "--source", $Source,
        "--chapter", $Chapter,
        "--type", $Type,
        "--timeline", $Timeline,
        "--story-config", $StoryConfigPath
    )
    if ($ByScene) { $distArgs += "--by-scene" }
    if ($DryRun) { $distArgs += "--dry-run" }
    & $python @distArgs
}
