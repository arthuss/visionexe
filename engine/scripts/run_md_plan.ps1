param (
    [string]$Plan = "",
    [int]$Timeline = 1,
    [string]$TimelineFolder = "",
    [string]$PlanName = "scene_01_01.json",
    [string]$StoryRoot = "",
    [string]$StoryConfig = "",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8123,
    [switch]$DryRun
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot

Set-Location -Path $RepoRoot
$OutputEncoding = [System.Text.Encoding]::UTF8

if (-not $Plan) {
    if ($StoryConfig) {
        $StoryConfigPath = (Resolve-Path -LiteralPath $StoryConfig).Path
        if (-not $StoryRoot) {
            $StoryRoot = Split-Path -Parent (Split-Path -Parent $StoryConfigPath)
        }
    } else {
        if (-not $StoryRoot) {
            $engineConfigPath = Join-Path $RepoRoot "engine\\config\\engine_config.json"
            $engineConfig = Get-Content -Path $engineConfigPath -Raw | ConvertFrom-Json
            $StoryRoot = $engineConfig.default_story_root
        }
        if (-not [System.IO.Path]::IsPathRooted($StoryRoot)) {
            $StoryRoot = Join-Path $RepoRoot $StoryRoot
        }
        $StoryConfigPath = Join-Path $StoryRoot "config\\story_config.json"
    }

    if (-not (Test-Path -LiteralPath $StoryConfigPath)) {
        Write-Host "FEHLER: story_config.json nicht gefunden: $StoryConfigPath" -ForegroundColor Red
        exit 1
    }

    $storyConfig = Get-Content -Path $StoryConfigPath -Raw | ConvertFrom-Json
    $subjectsRoot = $storyConfig.subjects_root
    if (-not $subjectsRoot) {
        $subjectsRoot = Join-Path $StoryRoot "subjects"
    }
    if (-not [System.IO.Path]::IsPathRooted($subjectsRoot)) {
        $subjectsRoot = Join-Path $RepoRoot $subjectsRoot
    }

    if (-not $TimelineFolder) {
        $timelineLabel = if ($storyConfig.timeline_label) { $storyConfig.timeline_label } else { "timeline" }
        $timelinePad = if ($storyConfig.timeline_index_padding) { [int]$storyConfig.timeline_index_padding } else { 2 }
        $timelineTag = $Timeline.ToString(("D{0}" -f $timelinePad))
        $TimelineFolder = "{0}_{1}" -f $timelineLabel, $timelineTag
    }

    $Plan = Join-Path $subjectsRoot ("timelines\\{0}\\md_plans\\{1}" -f $TimelineFolder, $PlanName)
}

if (-not (Test-Path -LiteralPath $Plan)) {
    Write-Host "FEHLER: MD-Plan nicht gefunden: $Plan" -ForegroundColor Red
    exit 1
}

$args = @("--plan", $Plan, "--host", $Host, "--port", $Port)
if ($DryRun) {
    $args += "--dry-run"
}

Write-Host "--- Motion Director Plan ---" -ForegroundColor Cyan
Write-Host "Plan:     $Plan" -ForegroundColor DarkGray
Write-Host "Host:     $Host" -ForegroundColor DarkGray
Write-Host "Port:     $Port" -ForegroundColor DarkGray

python engine/workers/md_record_sequence.py @args
