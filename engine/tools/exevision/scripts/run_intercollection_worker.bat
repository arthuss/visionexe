@echo off
setlocal

REM run_intercollection_worker.bat - wrapper for run_intercollection_worker.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_intercollection_worker.ps1" %*

endlocal
