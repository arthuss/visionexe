@echo off
setlocal

REM stop_vector_stack.bat - wrapper for stop_vector_stack.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop_vector_stack.ps1" %*

endlocal
