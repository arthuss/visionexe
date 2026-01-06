param (
    [int]$Start = 1,
    [int]$End = 108,
    [string]$Model = "",
    [string]$StoryRoot = "",
    [string]$StoryConfig = "",
    [switch]$DryRun,
    [switch]$SanitizeFirst,
    [string]$SanitizeReport = "",
    [switch]$FixHeadersFirst,
    [string]$FixHeadersReport = "",
    [switch]$RunRegieFix,
    [switch]$RegieOverwrite,
    [switch]$RegieDryRun
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

$sanitizeScript = Join-Path $RepoRoot "engine\\workers\\screenplay_sanitizer.py"
$headerFixScript = Join-Path $RepoRoot "engine\\workers\\scene_header_fixer.py"
$preflightScript = Join-Path $RepoRoot "engine\\workers\\scene_preflight_check.py"
$preflightOutput = Join-Path $env:TEMP "visionexe_scene_preflight.json"

if ($SanitizeFirst) {
    $sanitizeArgs = @($sanitizeScript, "--story-config", $StoryConfigPath, "--start", $Start, "--end", $End)
    if ($DryRun) { $sanitizeArgs += "--dry-run" }
    if ($SanitizeReport) { $sanitizeArgs += @("--output", $SanitizeReport) }
    python @sanitizeArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Sanitizer fehlgeschlagen." -ForegroundColor Red
        exit 1
    }
}

if ($FixHeadersFirst) {
    $fixArgs = @($headerFixScript, "--story-config", $StoryConfigPath, "--start", $Start, "--end", $End)
    if ($DryRun) { $fixArgs += "--dry-run" }
    if ($FixHeadersReport) { $fixArgs += @("--output", $FixHeadersReport) }
    python @fixArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Header-Fixer fehlgeschlagen." -ForegroundColor Red
        exit 1
    }
}

python $preflightScript --story-config $StoryConfigPath --start $Start --end $End --output $preflightOutput
if ($LASTEXITCODE -ne 0) {
    Write-Host "Preflight fehlgeschlagen." -ForegroundColor Red
    exit 1
}

$report = Get-Content -Path $preflightOutput -Raw | ConvertFrom-Json
$chapters = @()
if ($report.missing) { $chapters += $report.missing }
if ($report.invalid) { $chapters += $report.invalid }
$chapterList = $chapters | ForEach-Object { $_.chapter } | Sort-Object -Unique

if (-not $chapterList -or $chapterList.Count -eq 0) {
    Write-Host "Keine fehlenden/ungueltigen Kapitel gefunden." -ForegroundColor Green
    exit 0
}

Write-Host "Zu regenerierende Kapitel: $($chapterList -join ', ')" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DryRun: Keine Generierung gestartet." -ForegroundColor DarkGray
    exit 0
}

$drehbuchScript = Join-Path $RepoRoot "engine\\workers\\drehbuch.py"
foreach ($chapter in $chapterList) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $chapter" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    if ($Model) {
        python $drehbuchScript $chapter --model $Model --story-config $StoryConfigPath
    } else {
        python $drehbuchScript $chapter --story-config $StoryConfigPath
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! FEHLER in Kapitel $chapter !!!" -ForegroundColor Red
        Write-Host "Der Agent hat abgebrochen. Druecke eine Taste zum Weitermachen oder STRG+C zum Abbrechen..." -ForegroundColor White
        Start-Sleep -Seconds 3
    } else {
        Write-Host "Erfolg: Kapitel $chapter abgeschlossen." -ForegroundColor Green
    }

    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Regeneration abgeschlossen." -ForegroundColor Cyan

if ($RunRegieFix) {
    $regieFixScript = Join-Path $RepoRoot "engine\\scripts\\run_regie_fix.ps1"
    $regieArgs = @("-StoryConfig", $StoryConfigPath, "-Start", $Start, "-End", $End)
    if ($RegieOverwrite) { $regieArgs += "-OverwriteRegie" }
    if ($RegieDryRun -or $DryRun) { $regieArgs += "-DryRun" }
    & $regieFixScript @regieArgs
}
