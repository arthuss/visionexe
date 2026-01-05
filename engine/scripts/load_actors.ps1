param (
    [string[]]$Names,
    [string]$Queue = "",
    [string]$Prefer = "iavatar",
    [string]$StoryRoot = "",
    [string]$StoryConfig = "",
    [string]$LibraryRoot = "",
    [string]$IndexPath = "",
    [switch]$Index,
    [switch]$DryRun
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot

Set-Location -Path $RepoRoot
$OutputEncoding = [System.Text.Encoding]::UTF8

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

if (-not $Queue) {
    $Queue = Join-Path $subjectsRoot "actor_queue.jsonl"
}

$resolvedNames = @()
$preferMap = @{}

if ($Names) {
    $resolvedNames += $Names
} else {
    if (-not (Test-Path -LiteralPath $Queue)) {
        Write-Host "FEHLER: Queue nicht gefunden: $Queue" -ForegroundColor Red
        exit 1
    }
    foreach ($line in Get-Content -Path $Queue) {
        $trimmed = $line.Trim()
        if (-not $trimmed) {
            continue
        }
        try {
            $item = $trimmed | ConvertFrom-Json
        } catch {
            Write-Host "WARN: Ungueltige JSON-Zeile in Queue: $trimmed" -ForegroundColor Yellow
            continue
        }
        $name = $item.name
        if (-not $name) { $name = $item.actor_name }
        if (-not $name) { $name = $item.actor_id }
        if (-not $name) { $name = $item.id }
        if ($name) {
            $resolvedNames += $name
            if ($item.prefer) {
                $preferMap[$name] = $item.prefer
            }
        }
    }
}

$resolvedNames = $resolvedNames | Where-Object { $_ } | Select-Object -Unique
if (-not $resolvedNames) {
    Write-Host "FEHLER: Keine Actor-Namen gefunden." -ForegroundColor Red
    exit 1
}

Write-Host "--- VisionExe Actor Loader ---" -ForegroundColor Cyan
Write-Host "StoryConfig: $StoryConfigPath" -ForegroundColor DarkGray
Write-Host "Subjects:   $subjectsRoot" -ForegroundColor DarkGray
Write-Host "Queue:      $Queue" -ForegroundColor DarkGray
Write-Host "Actors:     $($resolvedNames -join ', ')" -ForegroundColor Gray

if ($Index) {
    $indexArgs = @()
    if ($LibraryRoot) {
        $indexArgs += "--library-root"
        $indexArgs += $LibraryRoot
    }
    if ($IndexPath) {
        $indexArgs += "--output"
        $indexArgs += $IndexPath
    }
    python engine/workers/reallusion_library_indexer.py @indexArgs
}

foreach ($actorName in $resolvedNames) {
    $actorPrefer = $Prefer
    if ($preferMap.ContainsKey($actorName)) {
        $actorPrefer = $preferMap[$actorName]
    }
    $payload = @{
        name = $actorName
        prefer = $actorPrefer
    }
    if ($IndexPath) { $payload.index_path = $IndexPath }
    if ($LibraryRoot) { $payload.library_root = $LibraryRoot }
    $payloadJson = $payload | ConvertTo-Json -Compress
    if ($DryRun) {
        Write-Host "DRYRUN: load_actor_by_name $actorName (prefer=$actorPrefer)" -ForegroundColor Yellow
        continue
    }
    python engine/workers/iclone_remote_client.py --action load_actor_by_name --payload $payloadJson
    Start-Sleep -Milliseconds 200
}
