param(
    [string]$Root = "",
    [string]$Config = "engine\\scripts\\rag_config_small.json",
    [string]$Extensions = "md,json,txt,csv",
    [int]$BatchSize = 8,
    [int]$MaxChars = 1800,
    [int]$Overlap = 200,
    [switch]$Reset,
    [switch]$KeepCheckpoint,
    [switch]$NoResume,
    [switch]$DryRun,
    [string]$StoryRoot = "",
    [string]$StoryConfig = ""
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot
Set-Location -Path $RepoRoot
$OutputEncoding = [System.Text.Encoding]::UTF8

if (-not $Root) {
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

    if (Test-Path -LiteralPath $StoryConfigPath) {
        $storyConfig = Get-Content -Path $StoryConfigPath -Raw | ConvertFrom-Json
        $dataRoot = $storyConfig.data_root
        if ($dataRoot) {
            if (-not [System.IO.Path]::IsPathRooted($dataRoot)) {
                $dataRoot = Join-Path $RepoRoot $dataRoot
            }
            $Root = Join-Path $dataRoot "raw"
        }
    }
}

if (-not $Root) {
    Write-Host "Root folder missing. Provide -Root or ensure story_config.json has data_root." -ForegroundColor Red
    exit 1
}

function Test-DockerReady {
    try {
        docker info --format "{{.ServerVersion}}" | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-DockerDesktop {
    $serviceNames = @("com.docker.service", "Docker Desktop Service")
    foreach ($name in $serviceNames) {
        $svc = Get-Service -Name $name -ErrorAction SilentlyContinue
        if ($svc -and $svc.Status -ne "Running") {
            Start-Service -Name $name -ErrorAction SilentlyContinue
        }
    }
    $dockerExe = "$Env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerExe) {
        Start-Process $dockerExe | Out-Null
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker CLI not found in PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-DockerReady)) {
    Write-Host "Docker not ready. Starting Docker Desktop..." -ForegroundColor Yellow
    Start-DockerDesktop
    $timeoutSec = 120
    $start = Get-Date
    while (-not (Test-DockerReady)) {
        Start-Sleep -Seconds 3
        if ((Get-Date) - $start -gt [TimeSpan]::FromSeconds($timeoutSec)) {
            Write-Host "Docker did not become ready within $timeoutSec seconds." -ForegroundColor Red
            exit 1
        }
    }
}

$containerName = "henoch-qdrant-small"
$existing = docker ps -a --filter "name=$containerName" --format "{{.ID}} {{.Status}}"
if (-not $existing) {
    Write-Host "Starting Qdrant container: $containerName" -ForegroundColor Cyan
    docker run -d -p 6337:6333 -p 6338:6334 --name $containerName qdrant/qdrant:v1.12.4 | Out-Null
} elseif ($existing -notmatch "Up") {
    Write-Host "Qdrant container exists but is stopped. Starting..." -ForegroundColor Cyan
    docker start $containerName | Out-Null
} else {
    Write-Host "Qdrant container already running." -ForegroundColor Green
}

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

$ragIndexer = Join-Path $RepoRoot "engine\\workers\\rag_indexer_folder.py"
$args = @(
    $ragIndexer,
    "--root", $Root,
    "--extensions", $Extensions,
    "--batch-size", $BatchSize,
    "--max-chars", $MaxChars,
    "--overlap", $Overlap
)
if ($configPath) { $args += @("--config", $configPath) }
if ($Reset) { $args += "--reset" }
if ($KeepCheckpoint) { $args += "--keep-checkpoint" }
if ($NoResume) { $args += "--no-resume" }
if ($DryRun) { $args += "--dry-run" }

Write-Host "Indexing folder: $Root" -ForegroundColor Yellow
python @args
