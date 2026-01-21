param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Host "dotnet is not available. Install .NET 10 first."
    exit 1
}

$root = Join-Path $PSScriptRoot "..\vector_mcp\VectorMcpServer"
Push-Location $root

if ($Args.Count -gt 0) {
    dotnet run @Args
} else {
    dotnet run
}

Pop-Location
