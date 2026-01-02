param(
    [string]$Root = "C:\\Users\\sasch\\visionexe\\stories\\template\\data\\raw",
    [string]$Config = "$PSScriptRoot\\rag_config_small.json",
    [string]$Extensions = "md,json,txt,csv",
    [int]$BatchSize = 8,
    [int]$MaxChars = 1800,
    [int]$Overlap = 200,
    [switch]$Reset,
    [switch]$KeepCheckpoint,
    [switch]$NoResume,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
$OutputEncoding = [System.Text.Encoding]::UTF8

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

$args = @(
    "rag_indexer_folder.py",
    "--root", $Root,
    "--config", $Config,
    "--extensions", $Extensions,
    "--batch-size", $BatchSize,
    "--max-chars", $MaxChars,
    "--overlap", $Overlap
)
if ($Reset) { $args += "--reset" }
if ($KeepCheckpoint) { $args += "--keep-checkpoint" }
if ($NoResume) { $args += "--no-resume" }
if ($DryRun) { $args += "--dry-run" }

Write-Host "Indexing folder: $Root" -ForegroundColor Yellow
python @args
