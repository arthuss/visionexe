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
    [string]$Model = ""
)

Set-Location -Path $PSScriptRoot

$OutputEncoding = [System.Text.Encoding]::UTF8

for ($i = $Start; $i -le $End; $i++) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $i / $End" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow

    if (-not $SkipRegie) {
        $regieArgs = @("regie_worker.py", $i)
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
        $audioArgs = @("audio_agent.py", $i)
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
