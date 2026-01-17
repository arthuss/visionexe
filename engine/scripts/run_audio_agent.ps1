param (
    [int]$Start = 1,
    [int]$End = 2,
    [switch]$Tts,
    [switch]$NoMonologue,
    [switch]$Force,
    [ValidateSet("plan","hybrid","gemini")]
    [string]$MonologueSource = "plan",
    [ValidateSet("scene","chapter","actor","both")]
    [string]$MonologueOutput = "chapter",
    [string]$Model = "",
    [string]$StoryRoot = "",
    [string]$StoryConfig = ""
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot
Set-Location -Path $RepoRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

if ($StoryConfig) {
    $StoryConfigPath = (Resolve-Path -LiteralPath $StoryConfig).Path
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

$storyConfig = Get-Content -Path $StoryConfigPath -Raw | ConvertFrom-Json -AsHashtable
if (-not $storyConfig) {
    Write-Host "FEHLER: story_config.json konnte nicht geladen werden: $StoryConfigPath" -ForegroundColor Red
    exit 1
}
if ($storyConfig -is [string]) {
    $trimmedConfig = $storyConfig.Trim()
    if ($trimmedConfig.StartsWith("{") -or $trimmedConfig.StartsWith("[")) {
        $storyConfig = $trimmedConfig | ConvertFrom-Json -AsHashtable
    }
}
function Get-StoryConfigValue {
    param (
        $Config,
        [string]$Key,
        $Default
    )
    if ($Config -is [System.Collections.IDictionary]) {
        if ($Config.ContainsKey($Key)) {
            $value = $Config[$Key]
            if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
                return $value
            }
        }
    } else {
        $prop = $Config.PSObject.Properties[$Key]
        if ($prop -and $null -ne $prop.Value -and -not [string]::IsNullOrWhiteSpace([string]$prop.Value)) {
            return $prop.Value
        }
    }
    return $Default
}

$filmsetsRoot = Get-StoryConfigValue -Config $storyConfig -Key "filmsets_root" -Default ""
if ([string]::IsNullOrWhiteSpace($filmsetsRoot)) {
    $configDir = Split-Path -Parent $StoryConfigPath
    $storyRootFallback = Split-Path -Parent $configDir
    $filmsetsRoot = Join-Path $storyRootFallback "filmsets"
    Write-Host "WARNUNG: filmsets_root fehlt in $StoryConfigPath -> Fallback: $filmsetsRoot" -ForegroundColor Yellow
}
$chapterLabel = Get-StoryConfigValue -Config $storyConfig -Key "chapter_label" -Default "chapter"
$chapterPadRaw = Get-StoryConfigValue -Config $storyConfig -Key "chapter_index_padding" -Default 3
$chapterPad = [int]$chapterPadRaw
if (-not [System.IO.Path]::IsPathRooted($filmsetsRoot)) {
    $filmsetsRoot = Join-Path $RepoRoot $filmsetsRoot
}
if (([string]::IsNullOrWhiteSpace($chapterLabel) -or $chapterLabel -eq "chapter") -and (Test-Path -LiteralPath $filmsetsRoot)) {
    $storyCandidate = Get-ChildItem -Path $filmsetsRoot -Directory -Filter "story_*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($storyCandidate) {
        $chapterLabel = "story"
    }
}
Write-Host "StoryConfig: $StoryConfigPath" -ForegroundColor DarkCyan
Write-Host "Filmsets:   $filmsetsRoot" -ForegroundColor DarkCyan
Write-Host "Label/Pad:  $chapterLabel / $chapterPad" -ForegroundColor DarkCyan

$audioScript = Join-Path $RepoRoot "engine\\workers\\audio_agent.py"

for ($i = $Start; $i -le $End; $i++) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $i / $End" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    $chapterFolder = Join-Path $filmsetsRoot ("{0}_{1}" -f $chapterLabel, $i.ToString(("D{0}" -f $chapterPad)))
    if (-not (Test-Path -LiteralPath $chapterFolder)) {
        if ($chapterLabel -ne "chapter") {
            $fallbackFolder = Join-Path $filmsetsRoot ("chapter_{0}" -f $i.ToString('000'))
            if (-not (Test-Path -LiteralPath $fallbackFolder)) {
                Write-Host "SKIPPING: Ordner $chapterFolder nicht gefunden." -ForegroundColor Magenta
                continue
            }
        } else {
            Write-Host "SKIPPING: Ordner $chapterFolder nicht gefunden." -ForegroundColor Magenta
            continue
        }
    }

    $args = @(
        $audioScript,
        $i,
        "--story-config",
        $StoryConfigPath,
        "--base-path",
        $filmsetsRoot,
        "--chapter-label",
        $chapterLabel,
        "--chapter-padding",
        $chapterPad
    )
    if (-not $Force) { $args += "--skip-existing" }
    if ($Tts) { $args += "--tts" }
    if ($NoMonologue) { $args += "--no-monologue" }
    if ($MonologueSource) { $args += @("--monologue-source", $MonologueSource) }
    if ($MonologueOutput) { $args += @("--monologue-output", $MonologueOutput) }
    if ($Model) { $args += @("--model", $Model) }

    python @args

    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! FEHLER in Kapitel $i !!!" -ForegroundColor Red
        Start-Sleep -Seconds 3
    } else {
        Write-Host "Erfolg: Kapitel $i abgeschlossen." -ForegroundColor Green
    }

    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Batch-Verarbeitung abgeschlossen." -ForegroundColor Cyan
