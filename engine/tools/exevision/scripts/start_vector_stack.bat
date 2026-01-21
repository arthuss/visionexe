@echo off
setlocal

REM start_vector_stack.bat - wrapper for start_vector_stack.ps1

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_vector_stack.ps1" %*

endlocal
