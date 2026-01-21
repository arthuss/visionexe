param (
    [int]$Start = 1,
    [int]$End = 108,
    [switch]$OverwriteRegie,
    [switch]$DryRunRegie,
    [switch]$SkipRegie,
    [switch]$SkipAudio,
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

$storyConfig = Get-Content -Path $StoryConfigPath -Raw | ConvertFrom-Json
$filmsetsRoot = $storyConfig.filmsets_root
if (-not [System.IO.Path]::IsPathRooted($filmsetsRoot)) {
    $filmsetsRoot = Join-Path $RepoRoot $filmsetsRoot
}
$chapterLabel = if ($storyConfig.chapter_label) { $storyConfig.chapter_label } else { "chapter" }
$chapterPad = if ($storyConfig.chapter_index_padding) { [int]$storyConfig.chapter_index_padding } else { 3 }

$regieScript = Join-Path $RepoRoot "engine\\workers\\regie_worker.py"
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

    if (-not $SkipRegie) {
        $regieArgs = @($regieScript, $i, "--story-config", $StoryConfigPath)
        if ($OverwriteRegie) { $regieArgs += "--overwrite" }
        if ($DryRunRegie) { $regieArgs += "--dry-run" }
        python @regieArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Host "!!! FEHLER in REGIE fuer Kapitel $i !!!" -ForegroundColor Red
            Start-Sleep -Seconds 3
            continue
        }
    }

    if (-not $SkipAudio) {
        $audioArgs = @($audioScript, $i, "--story-config", $StoryConfigPath)
        if (-not $Force) { $audioArgs += "--skip-existing" }
        if ($Tts) { $audioArgs += "--tts" }
        if ($NoMonologue) { $audioArgs += "--no-monologue" }
        if ($MonologueSource) { $audioArgs += @("--monologue-source", $MonologueSource) }
        if ($MonologueOutput) { $audioArgs += @("--monologue-output", $MonologueOutput) }
        if ($Model) { $audioArgs += @("--model", $Model) }
        python @audioArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Host "!!! FEHLER in AUDIO fuer Kapitel $i !!!" -ForegroundColor Red
            Start-Sleep -Seconds 3
            continue
        }
    }

    Write-Host "Erfolg: Kapitel $i abgeschlossen." -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Regie + Audio Batch abgeschlossen." -ForegroundColor Cyan
