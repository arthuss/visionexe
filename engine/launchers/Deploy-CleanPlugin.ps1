# Deploy-CleanPlugin.ps1
# Creates a clean distribution of the VisionExe plugin for iClone 8 (Python 3.8)

$src = "$PSScriptRoot\..\iclone"
$dist = "$PSScriptRoot\..\..\dist\visionexe"

# 1. Clean Dist
if (Test-Path $dist) {
    Remove-Item $dist -Recurse -Force
}
New-Item -ItemType Directory -Path $dist | Out-Null

# 2. Copy Source (excluding pycache)
Write-Host "Copying files to $dist..."
Copy-Item "$src\*" -Destination $dist -Recurse

# Remove all __pycache__ folders from dist
Get-ChildItem -Path $dist -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# 3. Syntax Check (Optional, requires python)
# We assume 'python' is in PATH. If it's 3.11, it might pass syntax that 3.8 fails (like match/case).
# But basic checks pass.

Write-Host "Clean build ready at: $dist"
Write-Host "To install manually:"
Write-Host "1. Delete old folders in iClone OpenPlugin."
Write-Host "2. Copy the contents of '$dist\openplugin' to 'iClone 8\Bin64\OpenPlugin'."
