param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not available. Install Python 3.11+."
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "..\story_tools\story_loader.py"
python $scriptPath @Args
