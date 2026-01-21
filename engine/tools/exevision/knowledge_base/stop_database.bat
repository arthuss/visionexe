@echo off
echo.
echo =================================================
echo  Stoppe die lokale KI-Wissensdatenbank (Docker)...
echo =================================================
echo.

docker-compose down

echo.
echo Datenbank-Container wurde gestoppt.
pause