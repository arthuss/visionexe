param (
    [int]$Start = 1,
    [int]$End = 108,
    [switch]$OverwriteRegie,
    [switch]$DryRun,
    [switch]$ReportOnly,
    [string]$ReportOutput = "",
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

$preflightScript = Join-Path $RepoRoot "engine\\workers\\regie_preflight_check.py"
$preflightOutput = Join-Path $env:TEMP "visionexe_regie_preflight.json"

$preflightArgs = @($preflightScript, "--story-config", $StoryConfigPath, "--start", $Start, "--end", $End, "--output", $preflightOutput)
python @preflightArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "Regie-Preflight fehlgeschlagen." -ForegroundColor Red
    exit 1
}

$report = Get-Content -Path $preflightOutput -Raw | ConvertFrom-Json
$missing = @()
if ($report.missing_regie) {
    $missing = $report.missing_regie | ForEach-Object { $_ }
}
$chapterList = $missing | ForEach-Object { $_.chapter } | Sort-Object -Unique

if ($ReportOutput) {
    $reportPath = $ReportOutput
    if (-not [System.IO.Path]::IsPathRooted($reportPath)) {
        $reportPath = Join-Path $RepoRoot $reportPath
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host "Regie-Report gespeichert: $reportPath" -ForegroundColor DarkGray
}

if ($ReportOnly) {
    if (-not $chapterList -or $chapterList.Count -eq 0) {
        Write-Host "Keine fehlenden REGIE_JSON gefunden." -ForegroundColor Green
    } else {
        Write-Host "Fehlende REGIE_JSON in Kapiteln: $($chapterList -join ', ')" -ForegroundColor Yellow
        foreach ($entry in $missing) {
            if ($entry.missing_scenes) {
                Write-Host ("- {0}: {1}" -f $entry.chapter, ($entry.missing_scenes -join ", ")) -ForegroundColor DarkGray
            }
        }
    }
    exit 0
}

if (-not $chapterList -or $chapterList.Count -eq 0) {
    Write-Host "Keine fehlenden REGIE_JSON gefunden." -ForegroundColor Green
    exit 0
}

Write-Host "Regie-Fix fuer Kapitel: $($chapterList -join ', ')" -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "DryRun: Keine Regie-Generierung gestartet." -ForegroundColor DarkGray
    exit 0
}

$regieScript = Join-Path $RepoRoot "engine\\workers\\regie_worker.py"
foreach ($chapter in $chapterList) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $chapter" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    $regieArgs = @($regieScript, $chapter, "--story-config", $StoryConfigPath)
    if ($OverwriteRegie) { $regieArgs += "--overwrite" }
    python @regieArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! FEHLER in REGIE fuer Kapitel $chapter !!!" -ForegroundColor Red
        Start-Sleep -Seconds 3
        continue
    }
    Write-Host "Regie-Fix abgeschlossen fuer Kapitel $chapter." -ForegroundColor Green
    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Regie-Fix abgeschlossen." -ForegroundColor Cyan
