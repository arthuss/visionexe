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
    [string]$Model = ""
)

Set-Location -Path $PSScriptRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

for ($i = $Start; $i -le $End; $i++) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $i / $End" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    $args = @("audio_agent.py", $i)
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
