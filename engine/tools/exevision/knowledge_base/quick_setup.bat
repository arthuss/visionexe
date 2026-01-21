@echo off
REM quick_setup.bat - Komplettes Setup mit einem Klick
echo.
echo ========================================
echo 🚀 KI KNOWLEDGE BASE - QUICK SETUP
echo ========================================
echo.

REM Prüfe Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python ist nicht verfügbar!
    echo    Bitte installiere Python 3.11+ und füge es zum PATH hinzu.
    pause
    exit /b 1
)

echo ✅ Python ist verfügbar
echo.

REM Installiere Requirements
echo 📦 Installiere Python-Abhängigkeiten...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Fehler beim Installieren der Abhängigkeiten!
    pause
    exit /b 1
)

echo ✅ Abhängigkeiten installiert
echo.

REM Starte Datenbank
echo 🚀 Starte Datenbank...
call start_knowledge_base.bat

REM Setup Datenbank
echo 🔧 Richte Datenbank ein...
python setup_database.py

if %errorlevel% neq 0 (
    echo ❌ Datenbank-Setup fehlgeschlagen!
    pause
    exit /b 1
)

echo.
echo ✅ SETUP ERFOLGREICH ABGESCHLOSSEN! 
echo.
echo 🎯 Du kannst jetzt:
echo    - 'python manage_database.py' für Verwaltung
echo    - 'python query_database.py' für Suchen
echo    - 'python ingest_assets.py' für Asset-Import
echo.
pause
