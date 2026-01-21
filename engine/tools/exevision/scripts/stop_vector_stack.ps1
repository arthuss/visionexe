param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

$root = Join-Path $PSScriptRoot "..\vector_mcp"
Push-Location $root

docker compose down

Pop-Location
