@echo off
setlocal

REM run_mcp_server.bat - wrapper for run_mcp_server.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_mcp_server.ps1" %*

endlocal
