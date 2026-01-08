param(
    [string]$StoryConfig = "stories/template/config/story_config.json",
    [string[]]$Timeline = @(),
    [string[]]$Workflows = @(
        "engine/workflows/TEXT_TO_IMG.json",
        "engine/workflows/zimage.json",
        "engine/workflows/flux_schnell.json",
        "engine/workflows/juggernaut.json"
    ),
    [string]$Python = "python",
    [string]$QueueOut = "",
    [string]$PropQueueOut = "",
    [string]$TrainingSetOut = "",
    [switch]$StartComfy = $true,
    [string]$ComfyScript = "engine/scripts/start_comfyui314wsl.ps1",
    [string]$ComfyWorkspace = "",
    [switch]$NoOrchestrator,
    [switch]$NoSkipExisting
)

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
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($PathValue, $ContentValue, $utf8NoBom)
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\\..")

$configPath = Resolve-RepoPath $StoryConfig $repoRoot
if (-not (Test-Path -LiteralPath $configPath)) {
    Write-Host "FEHLER: story_config.json nicht gefunden: $configPath" -ForegroundColor Red
    exit 1
}

$storyConfig = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$queuePath = Resolve-RepoPath ($QueueOut ? $QueueOut : $storyConfig.lora_training_queue_path) $repoRoot
$propQueuePath = Resolve-RepoPath ($PropQueueOut ? $PropQueueOut : $storyConfig.lora_prop_queue_path) $repoRoot
$trainingSetPath = Resolve-RepoPath ($TrainingSetOut ? $TrainingSetOut : $storyConfig.lora_training_set_path) $repoRoot

if (-not $queuePath) {
    Write-Host "FEHLER: lora_training_queue_path ist nicht gesetzt." -ForegroundColor Red
    exit 1
}
if (-not $propQueuePath) {
    Write-Host "FEHLER: lora_prop_queue_path ist nicht gesetzt." -ForegroundColor Red
    exit 1
}
if (-not $trainingSetPath) {
    Write-Host "FEHLER: lora_training_set_path ist nicht gesetzt." -ForegroundColor Red
    exit 1
}

$subjectsRoot = Resolve-RepoPath ($storyConfig.subjects_root ? $storyConfig.subjects_root : "stories/template/subjects") $repoRoot
$timelineLabel = $storyConfig.timeline_label ? $storyConfig.timeline_label : "timeline"
$timelinePadding = $storyConfig.timeline_index_padding ? [int]$storyConfig.timeline_index_padding : 2

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

if ($timelineTags.Count -gt 1) {
    Write-Host "Hinweis: Mehrere Timelines gefunden. lora_training_set.json wird nur einmal geschrieben." -ForegroundColor DarkYellow
}
}

$tempRoot = Join-Path $env:TEMP ("vx_lora_multi_workflow_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
New-Item -ItemType Directory -Path $tempRoot | Out-Null

$allQueue = @()
$allPropQueue = @()
$trainingSetWritten = $false

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
        $tmpPropQueue = Join-Path $tempRoot ("prop_queue_" + ($i + 1) + "_" + $timelineSuffix + ".json")
        $tmpTrainingSet = if (-not $trainingSetWritten) { $trainingSetPath } else { Join-Path $tempRoot ("training_set_" + ($i + 1) + "_" + $timelineSuffix + ".json") }

        $args = @(
            "engine/workers/lora_dynamic_queue_builder.py",
            "--story-config", $configPath,
            "--timeline", $timelineTag,
            "--style-seed-workflow", $workflowPath,
            "--output-queue", $tmpQueue,
            "--output-prop-queue", $tmpPropQueue,
            "--output-set", $tmpTrainingSet
        )

        & $Python @args
        if ($LASTEXITCODE -ne 0) {
            Write-Host "FEHLER: Queue-Builder fehlgeschlagen fuer $workflowPath (timeline $timelineTag)" -ForegroundColor Red
            exit $LASTEXITCODE
        }

        if (-not $trainingSetWritten) {
            $trainingSetWritten = $true
        }

        if (Test-Path -LiteralPath $tmpQueue) {
            $queueData = Get-Content -LiteralPath $tmpQueue -Raw | ConvertFrom-Json
            if ($queueData) {
                $allQueue += @($queueData)
            }
        }

        if (Test-Path -LiteralPath $tmpPropQueue) {
            $propData = Get-Content -LiteralPath $tmpPropQueue -Raw | ConvertFrom-Json
            if ($propData) {
                $allPropQueue += @($propData)
            }
        }
    }
}

$queueJson = $allQueue | ConvertTo-Json -Depth 50
$propQueueJson = $allPropQueue | ConvertTo-Json -Depth 50

Write-Utf8File -PathValue $queuePath -ContentValue $queueJson
Write-Utf8File -PathValue $propQueuePath -ContentValue $propQueueJson

Write-Host "Queue geschrieben: $queuePath" -ForegroundColor Green
Write-Host "Prop-Queue geschrieben: $propQueuePath" -ForegroundColor Green

if ($StartComfy) {
    $comfyScriptPath = Resolve-RepoPath $ComfyScript $repoRoot
    if (-not (Test-Path -LiteralPath $comfyScriptPath)) {
        Write-Host "FEHLER: ComfyUI Script nicht gefunden: $comfyScriptPath" -ForegroundColor Red
        exit 1
    }
    $comfyArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$comfyScriptPath`""
    Start-Process -FilePath "powershell" -ArgumentList $comfyArgs -WorkingDirectory $repoRoot | Out-Null
    Write-Host "ComfyUI gestartet: $comfyScriptPath" -ForegroundColor Green
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
