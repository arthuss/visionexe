param (
    [int]$Start = 1,
    [int]$End = 108,
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

    $args = @($audioScript, $i, "--story-config", $StoryConfigPath)
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
