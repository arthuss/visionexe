param(
    [ValidateSet("Junction", "Copy")]
    [string]$Mode = "Junction",
    [string]$TargetPath = "C:\\Program Files\\Reallusion\\iClone 8\\Bin64\\OpenPlugin"
)

function Resolve-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$repoRoot = Resolve-RepoRoot
$sourceRoot = Join-Path $repoRoot "engine\\iclone\\openplugin"

if (-not (Test-Path $sourceRoot)) {
    Write-Error "OpenPlugin source not found: $sourceRoot"
    exit 1
}

if (-not (Test-Path $TargetPath)) {
    Write-Error "OpenPlugin target not found: $TargetPath"
    exit 1
}

$folders = Get-ChildItem -Path $sourceRoot -Directory
if (-not $folders) {
    Write-Error "No plugin folders found in $sourceRoot"
    exit 1
}

Write-Host "Installing OpenPlugin wrappers from $sourceRoot to $TargetPath"
Write-Host "Mode: $Mode"

foreach ($folder in $folders) {
    $dest = Join-Path $TargetPath $folder.Name
    if (Test-Path $dest) {
        Write-Warning "Target exists, skipping: $dest"
        continue
    }

    if ($Mode -eq "Junction") {
        try {
            New-Item -ItemType Junction -Path $dest -Target $folder.FullName | Out-Null
            Write-Host "Linked: $dest -> $($folder.FullName)"
        } catch {
            Write-Warning "Failed to create junction (try running as admin): $dest"
            Write-Warning $_.Exception.Message
        }
    } else {
        try {
            Copy-Item -Path $folder.FullName -Destination $dest -Recurse
            Write-Host "Copied: $dest"
        } catch {
            Write-Warning "Failed to copy: $dest"
            Write-Warning $_.Exception.Message
        }
    }
}

Write-Host "Done. Restart iClone to see new plugins."
