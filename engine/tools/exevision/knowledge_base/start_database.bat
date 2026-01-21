@echo off
echo.
echo =================================================
echo  Starte die lokale KI-Wissensdatenbank (Docker)...
echo =================================================
echo.

docker-compose up -d

echo.
echo Datenbank-Container wird gestartet.
echo Du kannst den Status mit 'docker ps' ueberpruefen.
echo Die Datenbank ist erreichbar unter: localhost:5433
pause