param(
    [string]$RepoRoot
)

function Resolve-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$root = if ($RepoRoot) { $RepoRoot } else { Resolve-RepoRoot }
$configPath = Join-Path $root "engine\iclone\iclone_config.json"

[Environment]::SetEnvironmentVariable("VISIONEXE_ROOT", $root, "User")
[Environment]::SetEnvironmentVariable("ICLONE_CONFIG_PATH", $configPath, "User")

Write-Host "Set VISIONEXE_ROOT=$root"
Write-Host "Set ICLONE_CONFIG_PATH=$configPath"
Write-Host "Restart iClone to pick up the environment variables."
