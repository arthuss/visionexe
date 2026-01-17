param (
    [int]$Start = 1,
    [int]$End = 2,
    [string]$Model = "",
    [string]$StoryRoot = "",
    [string]$StoryConfig = "",
    [switch]$Resume,
    [switch]$Sanitize,
    [switch]$FixHeaders
)

$ScriptRoot = $PSScriptRoot
$EngineRoot = Split-Path -Parent $ScriptRoot
$RepoRoot = Split-Path -Parent $EngineRoot

# Work from repo root so relative paths are stable.
Set-Location -Path $RepoRoot

Write-Host "--- EXEGET:OS BATCH ENGINE ---" -ForegroundColor Cyan
Write-Host "Verarbeite Kapitel $Start bis $End"
Write-Host "Arbeitsverzeichnis: $RepoRoot" -ForegroundColor Gray

# UTF-8 output for console.
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
$filmsetsRoot = $storyConfig.filmsets_root
if (-not $filmsetsRoot) {
    $filmsetsRoot = Join-Path $StoryRoot "filmsets"
}
if (-not [System.IO.Path]::IsPathRooted($filmsetsRoot)) {
    $filmsetsRoot = Join-Path $RepoRoot $filmsetsRoot
}
$chapterLabel = if ($storyConfig.chapter_label) { $storyConfig.chapter_label } else { "chapter" }
$chapterPad = if ($storyConfig.chapter_index_padding) { [int]$storyConfig.chapter_index_padding } else { 3 }

# If chapter_label is missing, try to infer it from existing filmset folders.
if (-not $storyConfig.chapter_label) {
    $storyProbe = Join-Path $filmsetsRoot ("story_{0}" -f (1).ToString(("D{0}" -f $chapterPad)))
    $chapterProbe = Join-Path $filmsetsRoot ("chapter_{0}" -f (1).ToString(("D{0}" -f $chapterPad)))
    if (Test-Path -LiteralPath $storyProbe) {
        $chapterLabel = "story"
    } elseif (Test-Path -LiteralPath $chapterProbe) {
        $chapterLabel = "chapter"
    }
}

Write-Host "StoryConfig: $StoryConfigPath" -ForegroundColor DarkGray
Write-Host "Filmsets:   $filmsetsRoot" -ForegroundColor DarkGray
Write-Host "Label/Pad:  $chapterLabel / $chapterPad" -ForegroundColor DarkGray

$drehbuchScript = Join-Path $RepoRoot "engine\\workers\\drehbuch.py"
$sanitizeScript = Join-Path $RepoRoot "engine\\workers\\screenplay_sanitizer.py"
$headerFixScript = Join-Path $RepoRoot "engine\\workers\\scene_header_fixer.py"

for ($i = $Start; $i -le $End; $i++) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $i / $End" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    $chapterFolder = Join-Path $filmsetsRoot ("{0}_{1}" -f $chapterLabel, $i.ToString(("D{0}" -f $chapterPad)))
    if (-not (Test-Path -LiteralPath $chapterFolder)) {
        if ($chapterLabel -ne "chapter") {
            $fallbackFolder = Join-Path $filmsetsRoot ("chapter_{0}" -f $i.ToString('000'))
            if (Test-Path -LiteralPath $fallbackFolder) {
                $chapterFolder = $fallbackFolder
            } else {
                Write-Host "SKIPPING: Ordner $chapterFolder nicht gefunden." -ForegroundColor Magenta
                continue
            }
        } else {
            Write-Host "SKIPPING: Ordner $chapterFolder nicht gefunden." -ForegroundColor Magenta
            continue
        }
    }

    if ($Resume) {
        $outputPath = Join-Path $chapterFolder "DREHBUCH_HOLLYWOOD.md"
        if (Test-Path -LiteralPath $outputPath) {
            Write-Host "SKIPPING (resume): $outputPath bereits vorhanden." -ForegroundColor DarkGray
            if ($Sanitize) {
                python $sanitizeScript --story-config $StoryConfigPath --start $i --end $i
            }
            if ($FixHeaders) {
                python $headerFixScript --story-config $StoryConfigPath --start $i --end $i
            }
            continue
        }
    }

    if ($Model) {
        python $drehbuchScript $i --model $Model --story-config $StoryConfigPath
    } else {
        python $drehbuchScript $i --story-config $StoryConfigPath
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! FEHLER in Kapitel $i !!!" -ForegroundColor Red
        Write-Host "Der Agent hat abgebrochen. Druecke eine Taste zum Weitermachen oder STRG+C zum Abbrechen..." -ForegroundColor White
        Start-Sleep -Seconds 3
    } else {
        Write-Host "Erfolg: Kapitel $i abgeschlossen." -ForegroundColor Green
        if ($Sanitize) {
            python $sanitizeScript --story-config $StoryConfigPath --start $i --end $i
        }
        if ($FixHeaders) {
            python $headerFixScript --story-config $StoryConfigPath --start $i --end $i
        }
    }

    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Batch-Verarbeitung abgeschlossen." -ForegroundColor Cyan
