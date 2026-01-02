param (
    [int]$Start = 60,
    [int]$End = 108,
    [string]$Model = ""
)

# 1. SICHERHEITSGURT: Sicherstellen, dass wir im Ordner des Scripts arbeiten
# Das verhindert, dass Python Pfade relativ zu System32 oder deinem User-Profil sucht.
Set-Location -Path $PSScriptRoot

Write-Host "--- EXEGET:OS BATCH ENGINE ---" -ForegroundColor Cyan
Write-Host "Verarbeite Kapitel $Start bis $End"
Write-Host "Arbeitsverzeichnis: $PSScriptRoot" -ForegroundColor Gray

# 2. UTF-8 Unterstützung für die Konsole (wichtig für die Ge'ez Zeichen/Umlaute)
$OutputEncoding = [System.Text.Encoding]::UTF8

for ($i = $Start; $i -le $End; $i++) {
    Write-Host "`n================================================================" -ForegroundColor Yellow
    Write-Host "   KAPITEL $i / $End" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Yellow
    
    # Prüfen, ob das Kapitel-Verzeichnis überhaupt existiert, bevor wir Python rufen
    $chapterFolder = "filmsets\chapter_$( $i.ToString('000') )"
    if (-not (Test-Path $chapterFolder)) {
        Write-Host "SKIPPING: Ordner $chapterFolder nicht gefunden." -ForegroundColor Magenta
        continue
    }

    # Führe das Python-Skript aus
    # Wir nutzen --% um sicherzugehen, dass Argumente sauber an Python gehen
    if ($Model) {
        python drehbuch_gemini.py $i --model $Model
    } else {
        python drehbuch_gemini.py $i
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! FEHLER in Kapitel $i !!!" -ForegroundColor Red
        Write-Host "Der Agent hat abgebrochen. Drücke eine Taste zum Weitermachen oder STRG+C zum Abbrechen..." -ForegroundColor White
        # Kurze Pause für den User zum Lesen, aber kein Hard-Stop
        Start-Sleep -Seconds 3
    } else {
        Write-Host "Erfolg: Kapitel $i abgeschlossen." -ForegroundColor Green
    }
    
    # Abkühlzeit für die API (verhindert Rate-Limits bei Gemini)
    Start-Sleep -Seconds 2
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "Batch-Verarbeitung abgeschlossen." -ForegroundColor Cyan
