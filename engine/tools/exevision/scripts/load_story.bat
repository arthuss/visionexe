@echo off
setlocal

REM load_story.bat - wrapper for load_story.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0load_story.ps1" %*

endlocal
