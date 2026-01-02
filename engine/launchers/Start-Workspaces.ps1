param(
    [string[]]$Id,
    [string[]]$Category,
    [switch]$List,
    [switch]$Run,
    [switch]$OpenFolder,
    [switch]$OpenReadme,
    [switch]$PrintApi,
    [string]$ConfigPath
)

function Resolve-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
}

$repoRoot = Resolve-RepoRoot
$defaultConfig = Join-Path $repoRoot "engine\config\workspaces.json"
$configPath = if ($ConfigPath) { $ConfigPath } else { $defaultConfig }

if (-not (Test-Path $configPath)) {
    Write-Error "Workspaces config not found: $configPath"
    exit 1
}

$raw = Get-Content -Path $configPath -Raw
$config = $raw | ConvertFrom-Json

function Format-ApiList($apis) {
    if (-not $apis -or $apis.Count -eq 0) {
        return "(no api configured)"
    }
    $lines = @()
    foreach ($api in $apis) {
        $base = if ($api.base_url) { $api.base_url } else { "" }
        $type = if ($api.type) { $api.type } else { "" }
        $id = if ($api.id) { $api.id } else { "" }
        $lines += "- $id $type $base".Trim()
    }
    return ($lines -join "`n")
}

if ($List -or ((-not $Id) -and (-not $Category))) {
    Write-Host "Available workspaces:" 
    foreach ($ws in $config.workspaces) {
        $label = "{0} ({1})" -f $ws.id, $ws.category
        Write-Host "- $label"
    }
    Write-Host "`nUse -Id <id> or -Category <name> to select."
    exit 0
}

$targets = $config.workspaces
if ($Id) {
    $targets = $targets | Where-Object { $Id -contains $_.id }
}
if ($Category) {
    $targets = $targets | Where-Object { $Category -contains $_.category }
}

if (-not $targets -or $targets.Count -eq 0) {
    Write-Error "No workspaces matched the selection."
    exit 1
}

foreach ($ws in $targets) {
    Write-Host "`n== $($ws.id) ==" 
    Write-Host "Name: $($ws.name)"
    Write-Host "Host: $($ws.host)"
    if ($ws.path) {
        Write-Host "Path: $($ws.path)"
    }
    if ($ws.windows_path) {
        Write-Host "Windows Path: $($ws.windows_path)"
    }
    if ($ws.readme) {
        Write-Host "README: $($ws.readme)"
    }
    if ($PrintApi) {
        Write-Host "API:" 
        Write-Host (Format-ApiList $ws.apis)
    }

    if ($OpenFolder) {
        $openPath = if ($ws.windows_path) { $ws.windows_path } else { $ws.path }
        if ($openPath) {
            Start-Process -FilePath $openPath
        }
    }

    if ($OpenReadme -and $ws.readme) {
        Start-Process -FilePath $ws.readme
    }

    if ($Run) {
        $command = $ws.start_command
        if (-not $command) {
            Write-Host "Start command not set. Update workspaces.json start_command to enable -Run."
            continue
        }
        if ($ws.host -eq "wsl") {
            $distro = if ($ws.distro) { $ws.distro } else { "Ubuntu" }
            $cwd = $ws.path
            $cmd = if ($cwd) { "cd $cwd; $command" } else { $command }
            wsl -d $distro -- bash -lc $cmd
        } else {
            Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $command
        }
    }
}
