@echo off
REM start_knowledge_base.bat - Startet die komplette KI Knowledge Base
echo.
echo ===================================
echo 🧠 KI KNOWLEDGE BASE STARTER
echo ===================================
echo.

REM Prüfe ob Docker läuft
echo Prüfe Docker-Status...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker ist nicht verfügbar!
    echo    Bitte starte Docker Desktop und versuche es erneut.
    pause
    exit /b 1
)

echo ✅ Docker ist verfügbar
echo.

REM Starte Datenbank-Container
echo 🚀 Starte PostgreSQL-Container...
docker-compose up -d

REM Warte kurz, damit der Container hochfahren kann
echo 📊 Warte 10 Sekunden auf Datenbankstart...
timeout /t 10 /nobreak >nul

REM Prüfe Container-Status
docker ps | findstr "local_ai_knowledge_base" >nul
if %errorlevel% equ 0 (
    echo ✅ Datenbank-Container läuft
) else (
    echo ⚠️  Container-Status unklar - prüfe mit 'docker ps'
)

echo.
echo 🎯 Nächste Schritte:
echo    1. Führe 'setup_database.py' aus (einmalig)
echo    2. Starte 'manage_database.py' für Verwaltung
echo    3. Nutze 'query_database.py' für Suchen
echo.
echo Container-Logs anzeigen: docker logs local_ai_knowledge_base
echo Container stoppen: docker-compose down
echo.
pause
