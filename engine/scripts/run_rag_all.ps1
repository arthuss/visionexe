param(
    [string]$Chapter = "all",
    [int]$BatchSize = 4,
    [int]$MaxChars = 1200,
    [int]$Overlap = 200,
    [switch]$Reset,
    [switch]$NoMedia
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

if (-not $env:RAG_EMBEDDING_URL) {
    $env:RAG_EMBEDDING_URL = "http://localhost:11434/api/embed"
}
if (-not $env:RAG_EMBEDDING_API) {
    $env:RAG_EMBEDDING_API = "ollama"
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

$containerName = "henoch-qdrant"
$existing = docker ps -a --filter "name=$containerName" --format "{{.ID}} {{.Status}}"
if (-not $existing) {
    Write-Host "Starting Qdrant container: $containerName" -ForegroundColor Cyan
    docker run -d -p 6335:6333 -p 6336:6334 --name $containerName qdrant/qdrant:v1.12.4 | Out-Null
} elseif ($existing -notmatch "Up") {
    Write-Host "Qdrant container exists but is stopped. Starting..." -ForegroundColor Cyan
    docker start $containerName | Out-Null
} else {
    Write-Host "Qdrant container already running." -ForegroundColor Green
}

$args = @(
    "rag_indexer.py",
    "--chapter", $Chapter,
    "--batch-size", $BatchSize,
    "--max-chars", $MaxChars,
    "--overlap", $Overlap
)
if ($Reset) { $args += "--reset" }
if ($NoMedia) { $args += "--no-media" }

Write-Host "Indexing chapters ($Chapter)..." -ForegroundColor Yellow
python @args
