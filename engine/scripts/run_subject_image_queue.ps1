param(
    [string]$StoryConfig = "stories/template/config/story_config.json",
    [string[]]$Timeline = @(),
    [string[]]$Workflows = @(
        "engine/workflows/TEXT_TO_IMG.json",
        "engine/workflows/zimage.json",
        "engine/workflows/flux_schnell.json",
        "engine/workflows/juggernaut.json"
    ),
    [int]$Repeats = 1,
    [string]$Python = "python",
    [string]$QueueOut = "",
    [switch]$StartComfy = $true,
    [string]$ComfyUrl = "http://127.0.0.1:8188",
    [int]$ComfyWaitSec = 120,
    [int]$ComfyPollSec = 3,
    [string]$ComfyScript = "engine/scripts/start_comfyui314wsl.ps1",
    [string]$ComfyWorkspace = "",
    [switch]$NoOrchestrator,
    [switch]$NoSkipExisting
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param(
        [string]$PathValue,
        [string]$RepoRoot
    )
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return $PathValue
    }
    return (Join-Path $RepoRoot $PathValue)
}

function Write-Utf8File {
    param(
        [string]$PathValue,
        [string]$ContentValue
    )
    $parent = Split-Path -Parent $PathValue
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($PathValue, $ContentValue, $utf8NoBom)
}

function Get-ConfigValue {
    param(
        [object]$Config,
        [string]$Name,
        [string]$DefaultValue
    )
    if ($null -eq $Config) {
        return $DefaultValue
    }
    $prop = $Config.PSObject.Properties[$Name]
    if ($null -eq $prop) {
        return $DefaultValue
    }
    $value = $prop.Value
    if ($null -eq $value) {
        return $DefaultValue
    }
    $text = [string]$value
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $DefaultValue
    }
    return $text
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\\..")

$configPath = Resolve-RepoPath $StoryConfig $repoRoot
if (-not (Test-Path -LiteralPath $configPath)) {
    Write-Host "FEHLER: story_config.json nicht gefunden: $configPath" -ForegroundColor Red
    exit 1
}

$storyConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$dataRoot = Get-ConfigValue -Config $storyConfig -Name "data_root" -DefaultValue "stories/template/data"
$defaultQueue = Join-Path $dataRoot "queues/asset_bible_queue.json"
$queueValue = if ($QueueOut) { $QueueOut } else { $defaultQueue }
$queuePath = Resolve-RepoPath $queueValue $repoRoot

if (-not $queuePath) {
    Write-Host "FEHLER: asset_bible_queue.json Pfad ist nicht gesetzt." -ForegroundColor Red
    exit 1
}

$subjectsRoot = Resolve-RepoPath (Get-ConfigValue -Config $storyConfig -Name "subjects_root" -DefaultValue "stories/template/subjects") $repoRoot
$timelineLabel = Get-ConfigValue -Config $storyConfig -Name "timeline_label" -DefaultValue "timeline"
$timelinePaddingValue = Get-ConfigValue -Config $storyConfig -Name "timeline_index_padding" -DefaultValue "2"
$timelinePadding = [int]$timelinePaddingValue

$timelineTags = @()
if ($Timeline -and $Timeline.Count -gt 0) {
    foreach ($entry in $Timeline) {
        if (-not [string]::IsNullOrWhiteSpace($entry)) {
            $timelineTags += $entry
        }
    }
} else {
    $timelineRoot = Join-Path $subjectsRoot "timelines"
    if (Test-Path -LiteralPath $timelineRoot) {
        $folders = Get-ChildItem -LiteralPath $timelineRoot -Directory
        foreach ($folder in $folders) {
            $name = $folder.Name
            if ($name.StartsWith("$timelineLabel`_")) {
                $tag = $name.Substring($timelineLabel.Length + 1)
                if (-not [string]::IsNullOrWhiteSpace($tag)) {
                    $timelineTags += $tag
                }
            }
        }
    }
    if (-not $timelineTags -or $timelineTags.Count -eq 0) {
        $timelineTags = @("1")
    }
}

$tempRoot = Join-Path $env:TEMP ("vx_subject_queue_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null

$allQueue = @()

for ($i = 0; $i -lt $Workflows.Count; $i++) {
    $workflowPath = Resolve-RepoPath $Workflows[$i] $repoRoot
    if (-not (Test-Path -LiteralPath $workflowPath)) {
        Write-Host "FEHLER: Workflow nicht gefunden: $workflowPath" -ForegroundColor Red
        exit 1
    }

    for ($t = 0; $t -lt $timelineTags.Count; $t++) {
        $timelineTag = $timelineTags[$t]
        $timelineSuffix = ($timelineTag -replace "[^A-Za-z0-9_-]", "_")
        $tmpQueue = Join-Path $tempRoot ("queue_" + ($i + 1) + "_" + $timelineSuffix + ".json")

        $args = @(
            "engine/workers/asset_bible_queue_builder.py",
            "--story-config", $configPath,
            "--timeline", $timelineTag,
            "--workflow", $workflowPath,
            "--repeats", $Repeats,
            "--output-queue", $tmpQueue
        )

        & $Python @args
        if ($LASTEXITCODE -ne 0) {
            Write-Host "FEHLER: Queue-Builder fehlgeschlagen fuer $workflowPath (timeline $timelineTag)" -ForegroundColor Red
            exit $LASTEXITCODE
        }

        if (Test-Path -LiteralPath $tmpQueue) {
            $queueData = Get-Content -LiteralPath $tmpQueue -Raw | ConvertFrom-Json
            if ($queueData) {
                $allQueue += @($queueData)
            }
        }
    }
}

$queueJson = $allQueue | ConvertTo-Json -Depth 50
Write-Utf8File -PathValue $queuePath -ContentValue $queueJson
Write-Host "Queue geschrieben: $queuePath" -ForegroundColor Green

if ($StartComfy) {
    $comfyScriptPath = Resolve-RepoPath $ComfyScript $repoRoot
    if (-not (Test-Path -LiteralPath $comfyScriptPath)) {
        Write-Host "FEHLER: ComfyUI Script nicht gefunden: $comfyScriptPath" -ForegroundColor Red
        exit 1
    }
    $comfyArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$comfyScriptPath`""
    Start-Process -FilePath "powershell" -ArgumentList $comfyArgs -WorkingDirectory $repoRoot | Out-Null
    Write-Host "ComfyUI gestartet: $comfyScriptPath" -ForegroundColor Green

    $deadline = (Get-Date).AddSeconds($ComfyWaitSec)
    $ready = $false
    while ((Get-Date) -lt $deadline) {
        try {
            $resp = Invoke-WebRequest -Uri $ComfyUrl -Method Get -TimeoutSec 5
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
                $ready = $true
                break
            }
        } catch {
            Start-Sleep -Seconds $ComfyPollSec
        }
    }
    if (-not $ready) {
        Write-Host "FEHLER: ComfyUI nicht erreichbar unter $ComfyUrl (Timeout nach $ComfyWaitSec s)." -ForegroundColor Red
        exit 1
    }
    Write-Host "ComfyUI bereit: $ComfyUrl" -ForegroundColor Green
}

if (-not $NoOrchestrator) {
    $orchArgs = @(
        "engine/workers/comfy_orchestrator.py",
        "--story-config", $configPath,
        "--queue", $queuePath
    )
    if ($ComfyWorkspace) {
        $orchArgs += @("--comfy-workspace", $ComfyWorkspace)
    }
    if ($NoSkipExisting) {
        $orchArgs += "--no-skip-existing"
    }
    & $Python @orchArgs
    exit $LASTEXITCODE
}
