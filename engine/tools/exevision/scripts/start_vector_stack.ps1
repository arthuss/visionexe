param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not available. Start Docker Desktop first."
    exit 1
}

$root = Join-Path $PSScriptRoot "..\vector_mcp"
Push-Location $root

if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env not found. Copy .env.example to .env and adjust ports."
}

docker compose up -d

Pop-Location
